"""Rescore existing cross-runtime JSONLs with the latest detector.

The runner captures the full agent response into result_snippet[:300]
and runs detection at write time. When detector regexes are updated,
existing JSONLs become stale: the data is still valid but the
`passed` / `routed` / `ic_result_present` flags reflect the old
detector.

This script reads the captured `result_snippet` (300 chars) plus
re-runs detect_ic_result and detect_portfolio_evidence on it. Note:
result_snippet is truncated, so this is a lower-bound rescore — if a
signal lives past char 300 we'll miss it. For a true rescore we'd
need to re-capture the full text, which means re-running the barrage.
The truncated rescore catches the common case (markers appear early).
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from cobol_barrage_cross_runtime import (  # noqa: E402
    DEFLECT_OK,
    detect_ic_result,
    detect_invocations,
    detect_portfolio_evidence,
    matches,
)


def rescore_row(r: dict) -> dict:
    # Prefer the full text if it's stored; fall back to the truncated snippet
    # for legacy rows that predate the result_text capture.
    text = r.get("result_text") or r.get("result_snippet", "")
    detected = detect_invocations(text)
    ic_present, ic_exit, ic_script = detect_ic_result(text)
    pe = detect_portfolio_evidence(text)

    expected = r.get("expected", [])
    is_deflect = expected == [DEFLECT_OK] or (DEFLECT_OK in expected and len(expected) == 1)
    has_deflect_option = DEFLECT_OK in expected

    routed = (
        (ic_present and (ic_exit == 0 or ic_exit is None))
        or any(matches(e, detected) for e in expected if e != DEFLECT_OK)
        or pe
    )
    if is_deflect:
        passed = not routed
    elif has_deflect_option:
        passed = True
    else:
        passed = routed

    out = dict(r)
    out["detected"] = detected
    out["ic_result_present"] = ic_present
    out["ic_result_exit"] = ic_exit
    out["ic_result_script"] = ic_script
    out["portfolio_evidence"] = pe
    out["routed"] = routed
    out["passed"] = passed
    out["rescored"] = True
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+", type=Path)
    args = ap.parse_args()
    for p in args.paths:
        rows = [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
        new_rows = [rescore_row(r) for r in rows]
        p.write_text("\n".join(json.dumps(r) for r in new_rows) + "\n")
        passed = sum(1 for r in new_rows if r["passed"])
        total = len(new_rows)
        print(f"{p.name}: {passed}/{total} = {100 * passed // max(total, 1)}%")


if __name__ == "__main__":
    main()
