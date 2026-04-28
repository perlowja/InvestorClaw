"""COBOL barrage cross-runtime runner — OpenClaw / ZeroClaw / Hermes.

Loads nlq-prompts.json (30 prompts), executes each against the named
runtime via `docker exec`, and scores by text-grepping the response
for invocations of the `investorclaw` command surface (9-tool modern
or legacy 22-command bare). Writes a per-runtime JSONL in the same
shape as the Claude Code v2.5.x reports.

Provider parity (per ~/.harness/lib/run_nl_pilot_crossruntime.sh
convention):
  - openclaw — native (GRAEAE consensus); no provider arg
  - zeroclaw — xai / grok-4-1-fast (parity with hermes)
  - hermes   — xai / grok-4-1-fast (parity with zeroclaw)

OpenClaw uses GRAEAE intentionally — the per-runtime gates in
nlq-prompts.json (openclaw 27/30 publish vs hermes 20/30) account
for the architectural difference.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

DEFLECT_OK = "DEFLECT_OK"

LEGACY_VERBS = (
    "holdings", "performance", "bonds", "fixed-income", "analyst", "news",
    "synthesize", "optimize", "report", "eod-report", "rebalance",
    "rebalance-tax", "scenario", "target", "lookup", "setup", "guardrails",
    "market", "news-plan", "session", "fa-topics", "update-identity",
    "run", "stonkmode", "check-updates", "ollama-setup", "help",
    "cashflow", "peer", "analysis",
)

MODERN_NOUNS = (
    "portfolio_view", "portfolio_compute", "portfolio_market",
    "portfolio_bonds", "portfolio_scenario", "portfolio_target",
    "portfolio_lookup", "portfolio_config", "portfolio_report",
)


IC_RESULT_INLINE_RE = re.compile(r"\bic_result\b[^\n\d]{0,40}(\d+)")
IC_RESULT_JSON_RE = re.compile(r'"ic_result"\s*:\s*\{[^}]*"exit_code"\s*:\s*(\d+)')
IC_RESULT_SCRIPT_RE = re.compile(r'"ic_result"\s*:\s*\{[^}]*"script"\s*:\s*"([^"]+)"')
SCRIPT_EXIT_RE = re.compile(
    r"(?:Verification:?\s*)?[`\"]?((?:fetch_|portfolio_|ic_|holdings_|optimize_|rebalance_|cashflow_|peer_|news_|analyst_|bonds_|market_|report_|scenario_|target_|lookup_)[a-z0-9_]+\.py)[`\"]?\s*\(?exit_code[:\s=]+(\d+)\)?",
    re.IGNORECASE,
)
DOLLAR_RE = re.compile(r"\$\s*[0-9][0-9,]*(?:\.\d+)?(?:\s*[KMB]|\s*million|\s*billion)?")
TICKER_RE = re.compile(r"\b(?:AAPL|MSFT|GOOGL|GOOG|AMZN|NVDA|META|TSLA|BRK|JPM|V|JNJ|UNH|XOM|HD|MA|PG|AVGO|CVX|MRK|LLY|ABBV|KO|PEP|COST|WMT|CSCO|NFLX|ADBE|ORCL|CRM|AMD|DDOG|RBLX|RIOT|MO)\b")


def detect_ic_result(text: str) -> Tuple[bool, int | None, str | None]:
    """Return (envelope_present, exit_code, script_name).

    InvestorClaw's runtime emits a verification envelope after each
    invocation. The shape varies by agent runtime:
      - JSON:    `{"ic_result": {"script": "...", "exit_code": 0, ...}}`  (Hermes verbose)
      - inline:  `(ic_result: 0)`  (older OpenClaw)
      - script verification: `Verification: fetch_holdings.py (exit_code: 0)`  (current OpenClaw)
    Any of these means the agent invoked the InvestorClaw skill.
    """
    j = IC_RESULT_JSON_RE.search(text)
    s = IC_RESULT_SCRIPT_RE.search(text)
    if j:
        return True, int(j.group(1)), (s.group(1) if s else None)
    sc = SCRIPT_EXIT_RE.search(text)
    if sc:
        return True, int(sc.group(2)), sc.group(1)
    m = IC_RESULT_INLINE_RE.search(text)
    if m:
        return True, int(m.group(1)), None
    return False, None, None


def detect_portfolio_evidence(text: str) -> bool:
    """Heuristic: did the agent's response contain portfolio data?

    Falls back to this signal when no explicit ic_result envelope is
    present. Agents like Hermes sometimes synthesize the result without
    echoing the verification line, but the data itself is still in the
    response — dollar amounts, ticker symbols, account references.
    Used only as a secondary signal; the explicit envelope wins when
    present.
    """
    dollar_hits = len(DOLLAR_RE.findall(text))
    ticker_hits = len(TICKER_RE.findall(text))
    # Require multiple hits so generic mentions ("$10 fee") don't count.
    return dollar_hits >= 3 or ticker_hits >= 2


def detect_invocations(text: str) -> List[str]:
    """Return canonical invocations the agent appears to have made.

    Matches `investorclaw <verb>`, `/investorclaw:<verb>`, and
    `portfolio_<noun>` mention forms. Used as a SECONDARY signal —
    most agents return a synthesized natural-language response that
    omits the underlying tool calls. The primary signal is the
    `ic_result` envelope (see detect_ic_result).
    """
    detected: List[str] = []
    seen: set = set()

    for noun in MODERN_NOUNS:
        for m in re.finditer(rf"\b{re.escape(noun)}\b\s*([^\n.;]*)", text):
            tail = m.group(1).strip()[:120]
            sect = re.search(r"section=([a-z][a-z0-9-]*)", tail)
            topic = re.search(r"topic=([a-z][a-z0-9-]*)", tail)
            sym = re.search(r"--symbol(?:\s+([A-Z]+))?", tail)
            acc = "--accounts" in tail
            tag = noun
            if sect:
                tag = f"{noun} section={sect.group(1)}"
                if topic:
                    tag = f"{tag} topic={topic.group(1)}"
            elif acc:
                tag = f"{noun} --accounts"
            elif sym:
                tag = f"{noun} --symbol"
                if sym.group(1):
                    tag = f"{tag} {sym.group(1)}"
            if tag not in seen:
                seen.add(tag)
                detected.append(tag)

    for verb in LEGACY_VERBS:
        if re.search(rf"\binvestorclaw\s+{re.escape(verb)}\b", text) or re.search(
            rf"/investorclaw:{re.escape(verb)}\b", text
        ):
            if verb not in seen:
                seen.add(verb)
                detected.append(verb)

    return detected


def matches(expected: str, detected: List[str]) -> bool:
    e = expected.strip()
    if e == DEFLECT_OK:
        return not detected
    # Exact tag match (e.g. "portfolio_view section=holdings")
    if e in detected:
        return True
    # Accept if the verb portion of expected is in detected
    head = e.split()[0]
    if head in detected:
        return True
    # Prefix match (e.g. expected "portfolio_lookup --symbol" matches "portfolio_lookup --symbol AAPL")
    for d in detected:
        if d.startswith(e) or e.startswith(d):
            return True
    return False


def pre_prompt_cleanup(runtime: str) -> None:
    """Best-effort cleanup of stale session state before invoking the agent.

    OpenClaw's GRAEAE agent stores per-session JSONL locks under
    ~/.openclaw/agents/main/sessions/. If a previous invocation crashed
    or was killed, the lock file persists and blocks every subsequent
    call (observed: a single stale lock cascaded into 9 consecutive
    FAILs in the v2.5.1 linux-x86-host openclaw barrage). We rm any stale
    .lock files before each prompt — the actual session JSONL stays so
    conversation history is preserved within a session.
    """
    if runtime == "openclaw":
        subprocess.run(
            ["docker", "exec", "openclaw-demo-linux-x86-host", "sh", "-c",
             "rm -f /home/node/.openclaw/agents/main/sessions/*.lock 2>/dev/null"],
            capture_output=True, timeout=10,
        )


def runtime_command(runtime: str, prompt: str, xai_key: str | None) -> List[str]:
    if runtime == "openclaw":
        return [
            "docker", "exec", "openclaw-demo-linux-x86-host",
            "openclaw", "agent", "--to", "+17777777710",
            "--message", prompt, "--timeout", "300",
        ]
    if runtime == "zeroclaw":
        return [
            "docker", "exec", "-e", f"XAI_API_KEY={xai_key or ''}",
            "zeroclaw-demo-linux-x86-host", "timeout", "180",
            "zeroclaw", "agent", "-p", "xai", "--model", "grok-4-1-fast",
            "-m", prompt,
        ]
    if runtime == "hermes":
        # Hermes' built-in provider list doesn't include Together; the
        # container's `inference.provider: custom:together` config block
        # isn't reachable via the chat CLI flags. Use xai/grok-4-1-fast,
        # which (a) is a working tool-call-capable model on this host,
        # (b) matches the original 10-prompt cross-runtime pilot
        # convention (~/.harness/lib/run_nl_pilot_crossruntime.sh).
        # OpenClaw uses Together MiniMax for narrative + gpu-host gemma4
        # for consult per the v2.5.x intent.
        return [
            "docker", "exec", "-e", f"XAI_API_KEY={xai_key or ''}",
            "hermes-demo-linux-x86-host", "timeout", "180",
            "/opt/hermes/.venv/bin/hermes", "chat",
            "-q", prompt, "--provider", "xai", "-m", "grok-4-1-fast", "--yolo",
        ]
    raise ValueError(f"unknown runtime: {runtime}")


def run_one(runtime: str, prompt_id: str, prompt: str, expected: List[str], xai_key: str | None) -> dict:
    pre_prompt_cleanup(runtime)
    cmd = runtime_command(runtime, prompt, xai_key)
    start = time.time()
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=320)
        elapsed_ms = int((time.time() - start) * 1000)
        text = (res.stdout or "") + "\n" + (res.stderr or "")
        exit_code = res.returncode
    except subprocess.TimeoutExpired:
        elapsed_ms = int((time.time() - start) * 1000)
        text = "(timeout)"
        exit_code = 124

    detected = detect_invocations(text)
    ic_present, ic_exit, ic_script = detect_ic_result(text)
    portfolio_evidence = detect_portfolio_evidence(text)

    is_deflect = expected == [DEFLECT_OK] or (DEFLECT_OK in expected and len(expected) == 1)
    has_deflect_option = DEFLECT_OK in expected

    routed = (ic_present and (ic_exit == 0 or ic_exit is None)) or any(
        matches(e, detected) for e in expected if e != DEFLECT_OK
    ) or portfolio_evidence

    if is_deflect:
        passed = not routed
    elif has_deflect_option:
        passed = True  # Either route or deflect is acceptable
    else:
        passed = routed

    return {
        "id": prompt_id,
        "prompt": prompt,
        "expected": expected,
        "detected": detected,
        "ic_result_present": ic_present,
        "ic_result_exit": ic_exit,
        "ic_result_script": ic_script,
        "portfolio_evidence": portfolio_evidence,
        "routed": routed,
        "passed": passed,
        "duration_ms": elapsed_ms,
        "exit_code": exit_code,
        "result_snippet": text[:300].replace("\n", " "),
        "result_text": text,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("runtime", choices=["openclaw", "zeroclaw", "hermes"])
    ap.add_argument("--nlq", default=os.environ.get("NLQ_JSON", "harness/cobol/nlq-prompts.json"))
    ap.add_argument("--out", default=None)
    ap.add_argument("--xai-key", default=os.environ.get("XAI_API_KEY"))
    args = ap.parse_args()

    today = datetime.now().strftime("%Y-%m-%d")
    out_path = Path(args.out or f"harness/reports/v2.5.1-linux-x86-host-{args.runtime}-cobol-{today}.jsonl")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("")

    nlq = json.loads(Path(args.nlq).read_text())
    prompts = nlq["prompts"]

    inter_prompt_delay_s = float(os.environ.get("INTER_PROMPT_DELAY_S", "5"))

    rows = []
    for i, p in enumerate(prompts):
        if i > 0 and inter_prompt_delay_s > 0:
            time.sleep(inter_prompt_delay_s)
        expected = p["expected_routes"].get("investorclaw", [])
        print(f"=== {p['id']} ===", file=sys.stderr)
        row = run_one(args.runtime, p["id"], p["prompt"], expected, args.xai_key)
        with out_path.open("a") as f:
            f.write(json.dumps(row) + "\n")
        rows.append(row)
        verdict = "PASS" if row["passed"] else "FAIL"
        print(f"  {verdict} detected={row['detected'] or '[none]'} ic_result={row['ic_result_present']} ({row['duration_ms']}ms)", file=sys.stderr)

    total = len(rows)
    passed = sum(1 for r in rows if r["passed"])
    gates = nlq.get("fleet_gates", {}).get(args.runtime, {})
    print(file=sys.stderr)
    print(f"=== SUMMARY: {args.runtime} ===", file=sys.stderr)
    print(f"InvestorClaw {nlq.get('version')} cross-runtime ({args.runtime}): {passed}/{total} = {100*passed//max(total,1)}%", file=sys.stderr)
    if gates:
        print(f"Gate: min_pass={gates.get('min_pass')} publish_bar={gates.get('publish_bar')}", file=sys.stderr)
    print(f"Output: {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
