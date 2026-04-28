"""Aggregate COBOL barrage scores across the fleet (4 runtimes).

Loads per-runtime JSONLs from harness/reports/ and emits both a
human-readable markdown release-evidence report and a machine-readable
JSON summary.

Inputs (auto-detected by glob):
  harness/reports/<version>-linux-x86-host-openclaw-cobol-<date>.jsonl
  harness/reports/<version>-linux-x86-host-zeroclaw-cobol-<date>.jsonl
  harness/reports/<version>-linux-x86-host-hermes-cobol-<date>.jsonl
  harness/reports/<version>-linux-x86-host-cobol-<date>.jsonl   (Claude Code; hostless name)
  (plus any -<pi-host>- entries when Pi auth is restored)

Output:
  harness/reports/<version>-fleet-aggregate-<date>.md
  harness/reports/<version>-fleet-aggregate-<date>.json

Per-runtime gates are read from harness/cobol/nlq-prompts.json under
fleet_gates. Each runtime is reported against its own gate; the fleet
verdict is the conjunction of all runtimes' min_pass gates passing.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

RUNTIMES = ("openclaw", "zeroclaw", "hermes", "claudecode")
RUNTIME_DISPLAY = {
    "openclaw": "OpenClaw",
    "zeroclaw": "ZeroClaw",
    "hermes": "Hermes",
    "claudecode": "Claude Code (InvestorClaude)",
}

# Two filename shapes:
#   <ver>-linux-x86-host-<runtime>-cobol-<date>.jsonl  (cross-runtime)
#   <ver>-linux-x86-host-cobol-<date>.jsonl            (Claude Code, no runtime token)
FNAME_RE = re.compile(
    r"^(?P<version>v\d+\.\d+\.\d+)-(?P<host>[a-z0-9]+)(?:-(?P<runtime>openclaw|zeroclaw|hermes))?-cobol-(?P<date>\d{4}-\d{2}-\d{2})(?:-[A-Za-z0-9-]+)?\.jsonl$"
)


def load_jsonl(path: Path) -> List[dict]:
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]


def parse_filename(p: Path) -> Optional[dict]:
    m = FNAME_RE.match(p.name)
    if not m:
        return None
    runtime = m.group("runtime") or "claudecode"
    return {
        "version": m.group("version"),
        "host": m.group("host"),
        "runtime": runtime,
        "date": m.group("date"),
        "path": p,
    }


def discover_reports(reports_dir: Path) -> Dict[str, dict]:
    """Pick the most-recent report per runtime. RESCORED/PARSER-BUG suffixed
    files are excluded (they're development artifacts, not release evidence)."""
    by_runtime: Dict[str, dict] = {}
    for p in reports_dir.glob("*.jsonl"):
        if "RESCORED" in p.name or "PARSER-BUG" in p.name:
            continue
        meta = parse_filename(p)
        if not meta:
            continue
        cur = by_runtime.get(meta["runtime"])
        if cur is None or meta["date"] > cur["date"]:
            by_runtime[meta["runtime"]] = meta
    return by_runtime


def score(rows: List[dict]) -> Tuple[int, int]:
    return sum(1 for r in rows if r.get("passed")), len(rows)


def gate_verdict(passed: int, total: int, gates: dict) -> Tuple[str, str]:
    if not gates:
        return ("UNGATED", "")
    pub = gates.get("publish_bar")
    minp = gates.get("min_pass")
    if pub is not None and passed >= pub:
        return ("PUBLISH", f"≥ {pub}/{total} publish_bar")
    if minp is not None and passed >= minp:
        return ("STRICT_PASS", f"≥ {minp}/{total} min_pass (below {pub} publish)")
    return ("FAIL", f"< {minp}/{total} min_pass")


def render_markdown(version: str, date: str, runtimes: Dict[str, dict], gates: Dict[str, dict]) -> str:
    out = []
    out.append(f"# COBOL Barrage Fleet Aggregate — InvestorClaw {version}")
    out.append("")
    out.append(f"**Run date:** {date}")
    out.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    out.append("")
    out.append("## Per-runtime scores")
    out.append("")
    out.append("| Runtime | Score | % | Gate | Verdict |")
    out.append("|---|---:|---:|---|---|")
    for rt in RUNTIMES:
        meta = runtimes.get(rt)
        gate = gates.get(rt, {})
        if meta is None:
            out.append(f"| {RUNTIME_DISPLAY[rt]} | — | — | publish≥{gate.get('publish_bar', '?')} / min≥{gate.get('min_pass', '?')} | **NOT RUN** |")
            continue
        rows = load_jsonl(meta["path"])
        passed, total = score(rows)
        pct = 100 * passed // max(total, 1)
        verdict, note = gate_verdict(passed, total, gate)
        out.append(f"| {RUNTIME_DISPLAY[rt]} | {passed}/{total} | {pct}% | publish≥{gate.get('publish_bar', '?')} / min≥{gate.get('min_pass', '?')} | **{verdict}** ({note}) |")
    out.append("")

    # Per-prompt cross-runtime grid
    out.append("## Per-prompt cross-runtime grid")
    out.append("")
    grid: Dict[str, Dict[str, dict]] = defaultdict(dict)
    for rt, meta in runtimes.items():
        for r in load_jsonl(meta["path"]):
            grid[r["id"]][rt] = r
    header = ["Prompt"] + [RUNTIME_DISPLAY[rt] for rt in RUNTIMES]
    out.append("| " + " | ".join(header) + " |")
    out.append("|" + "|".join(["---"] * len(header)) + "|")
    for pid in sorted(grid.keys()):
        cells = [pid]
        for rt in RUNTIMES:
            r = grid[pid].get(rt)
            if r is None:
                cells.append("—")
            else:
                cells.append("✓" if r.get("passed") else "✗")
        out.append("| " + " | ".join(cells) + " |")
    out.append("")

    fleet_pass = all(
        score(load_jsonl(meta["path"]))[0] >= gates.get(rt, {}).get("min_pass", 0)
        for rt, meta in runtimes.items()
    )
    missing = [rt for rt in RUNTIMES if rt not in runtimes]
    out.append("## Fleet verdict")
    out.append("")
    if missing:
        out.append(f"- **Incomplete fleet:** missing runtimes — {', '.join(RUNTIME_DISPLAY[m] for m in missing)}")
    if fleet_pass and not missing:
        out.append("- **Fleet PASS** — all runtimes cleared their min_pass gate")
    elif fleet_pass and missing:
        out.append("- **Available runtimes pass**, but fleet result is partial pending missing runtimes above")
    else:
        out.append("- **Fleet FAIL** — at least one runtime below its min_pass gate")
    out.append("")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reports-dir", default="harness/reports")
    ap.add_argument("--nlq", default="harness/cobol/nlq-prompts.json")
    ap.add_argument("--out", default=None, help="Output markdown path; .json sibling auto-generated")
    args = ap.parse_args()

    reports_dir = Path(args.reports_dir)
    nlq = json.loads(Path(args.nlq).read_text())
    gates = nlq.get("fleet_gates", {})
    version = nlq.get("version", "v?.?")
    runtimes = discover_reports(reports_dir)

    if not runtimes:
        print(f"no JSONL reports found in {reports_dir}")
        return 1

    today = datetime.now().strftime("%Y-%m-%d")
    out_md = Path(args.out or f"{reports_dir}/{version}-fleet-aggregate-{today}.md")
    out_json = out_md.with_suffix(".json")

    md = render_markdown(version, today, runtimes, gates)
    out_md.write_text(md)

    summary = {
        "version": version,
        "date": today,
        "runtimes": {},
        "fleet_pass": True,
    }
    for rt, meta in runtimes.items():
        rows = load_jsonl(meta["path"])
        passed, total = score(rows)
        gate = gates.get(rt, {})
        verdict, note = gate_verdict(passed, total, gate)
        summary["runtimes"][rt] = {
            "passed": passed,
            "total": total,
            "pct": 100 * passed // max(total, 1),
            "gate": gate,
            "verdict": verdict,
            "verdict_note": note,
            "report_path": str(meta["path"]),
        }
        if verdict == "FAIL":
            summary["fleet_pass"] = False
    summary["missing_runtimes"] = [rt for rt in RUNTIMES if rt not in runtimes]
    if summary["missing_runtimes"]:
        summary["fleet_pass"] = False

    out_json.write_text(json.dumps(summary, indent=2))
    print(f"wrote {out_md}")
    print(f"wrote {out_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
