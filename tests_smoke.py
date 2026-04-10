#!/usr/bin/env python3
"""Submission smoke test for InvestorClaw.

Checks the basics ClawHub reviewers and cold installs care about:
- required repo files exist
- plugin manifest parses and matches core metadata
- routed commands resolve to real scripts
- entrypoint help runs successfully
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent

REQUIRED_FILES = [
    "openclaw.plugin.json",
    "SKILL.md",
    "README.md",
    "LICENSE",
    "requirements.txt",
    "investorclaw.py",
    "index.ts",
]


def fail(msg: str) -> int:
    print(f"FAIL: {msg}")
    return 1


def ok(msg: str) -> None:
    print(f"OK: {msg}")


def main() -> int:
    for rel in REQUIRED_FILES:
        path = ROOT / rel
        if not path.exists():
            return fail(f"missing required file: {rel}")
        ok(f"found {rel}")

    plugin = json.loads((ROOT / "openclaw.plugin.json").read_text())
    if plugin.get("id") != "investorclaw":
        return fail("plugin id must be 'investorclaw'")
    ok("plugin id is investorclaw")

    if plugin.get("version") != "1.0.0":
        return fail("plugin version must be 1.0.0")
    ok("plugin version is 1.0.0")

    if plugin.get("homepage") != "https://github.com/perlowja/InvestorClaw":
        return fail("plugin homepage is not canonical GitHub URL")
    ok("plugin homepage matches canonical repo")

    oc = plugin.get("openclaw", {})
    if "./" not in oc.get("skills", []):
        return fail("openclaw.skills must include './'")
    ok("plugin skills entry present")

    sys.path.insert(0, str(ROOT))
    from runtime.router import COMMANDS, resolve_script  # noqa: WPS433

    scripts_dir = ROOT / "commands"
    for command in sorted(COMMANDS):
        script = resolve_script(command, scripts_dir)
        if script is None:
            return fail(f"command does not resolve: {command}")
        if not script.exists():
            return fail(f"resolved script missing for {command}: {script}")
    ok(f"resolved {len(COMMANDS)} commands")

    result = subprocess.run(
        [sys.executable, str(ROOT / "investorclaw.py"), "help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return fail(f"help command failed: {result.stderr.strip() or result.stdout.strip()}")
    if "Usage: /portfolio <command>" not in result.stdout:
        return fail("help output missing usage header")
    ok("entrypoint help command succeeded")

    # ------------------------------------------------------------------
    # Test: ic_result envelope present in guardrails output
    # ------------------------------------------------------------------
    ic_result = subprocess.run(
        [sys.executable, str(ROOT / "investorclaw.py"), "guardrails"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    combined = ic_result.stdout + ic_result.stderr
    if '"ic_result"' not in combined:
        return fail("ic_result envelope missing from guardrails output")
    ok("ic_result envelope present in guardrails output")

    # ------------------------------------------------------------------
    # Test: HMAC fingerprint returns 16-char hex string
    # ------------------------------------------------------------------
    sys.path.insert(0, str(ROOT))
    try:
        from internal.tier3_enrichment import _compute_fingerprint
        fp = _compute_fingerprint("MSFT", "gemma4-consult", "test synthesis")
        if len(fp) != 16:
            return fail(f"HMAC fingerprint wrong length: {len(fp)} (expected 16)")
        int(fp, 16)  # must be valid hex
    except Exception as e:
        return fail(f"HMAC fingerprint test failed: {e}")
    ok("HMAC fingerprint returns 16-char hex string")

    # ------------------------------------------------------------------
    # Test: dynamic consultation limit tiers
    # ------------------------------------------------------------------
    try:
        from services.consultation_policy import get_dynamic_consultation_limit
        cases = [(10, 10), (30, 30), (100, 40), (250, 20)]
        for position_count, expected in cases:
            got = get_dynamic_consultation_limit(position_count)
            if got != expected:
                return fail(f"get_dynamic_consultation_limit({position_count}) = {got}, expected {expected}")
    except Exception as e:
        return fail(f"dynamic consultation limit test failed: {e}")
    ok("dynamic consultation limit tiers correct")

    # ------------------------------------------------------------------
    # Test: enrichment_status defaults when no progress file
    # ------------------------------------------------------------------
    try:
        from services.consultation_policy import get_enrichment_status
        with tempfile.TemporaryDirectory() as tmp:
            status = get_enrichment_status(Path(tmp))
            if status.get("in_progress") is not False:
                return fail("enrichment_status in_progress should default to False")
    except Exception as e:
        return fail(f"enrichment_status defaults test failed: {e}")
    ok("enrichment_status defaults correct when no progress file")

    # ------------------------------------------------------------------
    # Test: compact synthesis_basis field and enrichment_status block
    # ------------------------------------------------------------------
    try:
        from rendering.compact_serializers import serialize_analyst_compact
        mock_payload = {
            "disclaimer": "EDUCATIONAL ANALYSIS - NOT INVESTMENT ADVICE",
            "timestamp": "2026-04-10T00:00:00",
            "total_symbols": 2,
            "recommendations": {
                "MSFT": {
                    "symbol": "MSFT",
                    "consensus": "Strong Buy",
                    "analyst_count": 54,
                    "current_price": 420.0,
                    "consultation": {"model": "gemma4-consult", "is_heuristic": False, "inference_ms": 3420},
                    "synthesis": "Analysts remain bullish on MSFT cloud growth.",
                    "key_insights": ["Strong Azure momentum"],
                    "risk_assessment": "Macro slowdown risk.",
                    "fingerprint": "abcd1234efgh5678",
                    "quote": {"text": "test", "attribution": "gemma4-consult", "verbatim_required": True, "fingerprint": "abcd1234efgh5678"},
                },
                "XYZ": {
                    "symbol": "XYZ",
                    "consensus": "Hold",
                    "analyst_count": 5,
                    "current_price": 10.0,
                },
            },
        }
        compact = serialize_analyst_compact(mock_payload)
        msft_basis = compact["recommendations"]["MSFT"].get("synthesis_basis")
        xyz_basis = compact["recommendations"]["XYZ"].get("synthesis_basis")
        if msft_basis != "enriched":
            return fail(f"MSFT synthesis_basis should be 'enriched', got {msft_basis!r}")
        if xyz_basis != "structured":
            return fail(f"XYZ synthesis_basis should be 'structured', got {xyz_basis!r}")
        if "enrichment_status" not in compact:
            return fail("enrichment_status block missing from compact output")
    except Exception as e:
        return fail(f"compact synthesis_basis test failed: {e}")
    ok("compact synthesis_basis and enrichment_status block correct")

    # ------------------------------------------------------------------
    # Test: INVESTORCLAW_CONSULTATION_HMAC_KEY in plugin configSchema
    # ------------------------------------------------------------------
    config_schema = plugin.get("configSchema", {})
    if "INVESTORCLAW_CONSULTATION_HMAC_KEY" not in config_schema:
        return fail("INVESTORCLAW_CONSULTATION_HMAC_KEY missing from plugin configSchema")
    ok("INVESTORCLAW_CONSULTATION_HMAC_KEY present in plugin configSchema")

    print("SMOKE_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
