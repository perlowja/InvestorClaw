#!/usr/bin/env python3
# Copyright 2026 InvestorClaw Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""InvestorClaw CLI shim — delegates to ic_engine.cli for back-compat.

Phase 2 of IC_DECOMPOSITION (v2.3.0): the CLI implementation lives in
ic-engine v2.4.1+. This module is a thin wrapper kept for callers that
still spawn this file directly or import names from this
module path:

    * server/investorclaw_api.py — FastAPI server. Imports get_version,
      spawns this script as a subprocess for command dispatch.
    * index.ts / dist/index.js — OpenClaw native plugin compatibility path.
    * Any user shell snippet that referenced the file path directly.

New callers should use the installed `investorclaw` entry point (provided
by this adapter via the `[project.scripts]` section in pyproject.toml).
This shim exists to avoid breaking existing integrations during the Phase 2
rollout; a future phase will rewire callers and may remove the shim.

Behavior:
  1. Sets INVESTORCLAW_SKILL_DIR to this file's directory (the adapter
     checkout) so ic-engine's CLI resolves user data (.env, portfolios/,
     etc.) under the adapter root rather than the engine package install.
  2. Loads the adapter checkout's .env (if present) into os.environ before
     delegating, so api keys and overrides are visible to the engine.
  3. Propagates the engine CLI's exit code via sys.exit(main()) so
     subprocess callers that key off returncode see real failures.
"""

import os
import sys
from pathlib import Path

# Adapter version literal. Kept here for harness/contract_check.py and other
# tooling that grep-parses a `VERSION = "..."` line; pyproject.toml is the
# canonical source of truth (the value here mirrors the pyproject entry).
# `__version__` is also exposed as a module attribute for `from investorclaw
# import __version__` callers preserved across the Phase 2 shim cut.
VERSION = "2.6.0"
__version__ = VERSION

_HERE = Path(__file__).resolve().parent


def _resolve_skill_dir() -> Path:
    """Find the adapter checkout — the dir holding `.env`, `portfolios/`,
    `claude/`, etc. Probed in this order so all InvestorClaw install paths
    (editable source, standalone clone, OpenClaw skill, Claude plugin)
    converge on the right answer:

      1. INVESTORCLAW_SKILL_DIR env override (explicit caller intent).
      2. _HERE if it has the checkout signature (pyproject.toml + SKILL.md
         at the same level). True for editable installs and direct script
         invocation from a clone. NOT true for non-editable wheel installs
         where `investorclaw.py` lands alone in site-packages.
      3. Common standalone clone location ~/InvestorClaw/.
      4. OpenClaw skill workspace ~/.openclaw/workspace/skills/investorclaw/.
      5. Last-resort fallback: _HERE — downstream commands will error
         clearly if the user-data files aren't actually there.
    """
    explicit = os.environ.get("INVESTORCLAW_SKILL_DIR", "").strip()
    if explicit:
        return Path(explicit).expanduser().resolve()

    def _looks_like_checkout(d: Path) -> bool:
        try:
            return (d / "pyproject.toml").exists() and (d / "SKILL.md").exists()
        except OSError:
            return False

    if _looks_like_checkout(_HERE):
        return _HERE

    for candidate in (
        Path.home() / "InvestorClaw",
        Path.home() / ".openclaw/workspace/skills/investorclaw",
    ):
        if _looks_like_checkout(candidate):
            return candidate.resolve()

    return _HERE


# Tell ic-engine v2.4.1+ where the adapter checkout lives. Set before any
# ic_engine import so cli.py's module-level SKILL_DIR resolution sees it.
# Always overwrite the env var with the resolved-and-normalized path so
# callers passing `~/foo` or relative dirs end up with an absolute string;
# ic_engine.cli treats the raw env-var literally and won't re-expand.
_SKILL_DIR = _resolve_skill_dir()
os.environ["INVESTORCLAW_SKILL_DIR"] = str(_SKILL_DIR)

# Load adapter-checkout .env from the resolved skill dir (NOT _HERE — for
# wheel installs _HERE points at site-packages, but the real .env lives in
# the user's clone resolved by _resolve_skill_dir above). python-dotenv
# ships transitively with ic-engine; if somehow unavailable we silently
# skip and let the engine's fallback paths handle missing env keys.
try:
    from dotenv import load_dotenv

    load_dotenv(_SKILL_DIR / ".env", override=False)
except ImportError:
    pass

# Helpful error message if the engine isn't installed in this interpreter.
# This path only fires when callers run the shim against a bare system Python;
# the installed `investorclaw` console script always uses the venv that has
# ic-engine present.
try:
    from ic_engine.cli import main  # noqa: E402  (delayed import is intentional)
except ImportError as _ic_engine_missing:
    sys.stderr.write(
        f"investorclaw: ic-engine is not installed in {sys.executable}.\n"
        "Use the installed CLI binary (resolves on PATH after `pip install .`):\n"
        "  $ investorclaw <command>\n"
        "Or install adapter + engine into the current interpreter:\n"
        "  $ pip install -r requirements.txt\n"
        f"\n(import error: {_ic_engine_missing})\n"
    )
    sys.exit(1)


def get_version() -> str:
    """Return the active adapter version string.

    Honors the INVESTORCLAW_VERSION env var override (matches the engine's
    semantics) but reports the *adapter* version, not the underlying
    engine — those version independently. Use `get_engine_version()` if
    you specifically need the engine.
    """
    return os.environ.get("INVESTORCLAW_VERSION", VERSION)


def get_canonical_version() -> str:
    """Return the canonical adapter version (ignores INVESTORCLAW_VERSION env).
    Pre-Phase-2 helper preserved for back-compat.
    """
    return VERSION


def is_development() -> bool:
    """True if the active version string contains '-dev'."""
    active = get_version()
    return "dev" in active.lower() or "-dev" in active


def get_engine_version() -> str:
    """Return the underlying ic-engine version. Phase 2 addition for callers
    that previously got both versions from a single get_version() call.
    """
    import ic_engine

    return ic_engine.__version__


if __name__ == "__main__":
    sys.exit(main())
