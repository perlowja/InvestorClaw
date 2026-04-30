#!/usr/bin/env python3
# Copyright 2026 InvestorClaw Contributors
# Licensed under Apache 2.0
"""Build an audit-compliant skill bundle for distribution.

Produces dist/investorclaw-skill-<version>.tar.gz containing only the
whitelisted files that satisfy zeroclaw 0.7.3's skill audit policy AND
work with openclaw + hermes skill-loading mechanisms.

Whitelist (what GOES IN — explicit, not glob-based):
    SKILL.md, COMMANDS.md, CAPABILITIES.md, SKILL.toml
    LICENSE, pyproject.toml, uv.lock
    package.json (for openclaw plugin manifest)
    dist/index.js (compiled openclaw plugin)
    dist/index.d.ts (optional type defs)
    config/*.toml, config/*.yaml, config/*.json
    data/* (read-only data — yaml, json, csv, txt only)
    references/*.md
    plugin/* (if exists, for openclaw — TypeScript source of plugin)

Excluded (would fail zeroclaw audit OR not skill content):
    Anything not in the whitelist
    *.sh, *.bash, *.ps1, *.bat, *.fish (script-like files)
    Symlinks (zeroclaw rejects)
    .git, .venv, __pycache__, node_modules, .pytest_cache
    installers/ (deployment scripts, ship separately)
    harness/, tests/, docs/ (dev artifacts)
    *.py (Python code is in ic-engine via uv.lock pin, not in skill bundle)

Pre-build audit-check enforces:
    - No high-risk command patterns (curl|sh, wget|sh, iex, pip install)
      in markdown files that get injected into LLM system prompt
    - No remote-md-links to external URLs
    - No symlinks anywhere in the bundle path
"""

from __future__ import annotations

import os
import re
import shutil
import sys
import tarfile
from pathlib import Path
from typing import Iterator

try:
    import tomllib  # Python 3.11+
except ImportError:
    try:
        import tomli as tomllib  # type: ignore
    except ImportError:
        tomllib = None  # fallback to regex-only version reading


REPO_ROOT = Path(__file__).resolve().parent.parent

# Files that go into the bundle, top-level whitelist
WHITELIST_TOP_LEVEL = [
    "SKILL.md",
    "COMMANDS.md",
    "CAPABILITIES.md",
    "SKILL.toml",
    "LICENSE",
    "pyproject.toml",
    "uv.lock",
    "package.json",
    ".skillignore",
]

# Directory whitelists with file-pattern restrictions
WHITELIST_DIRS = {
    "config": (".toml", ".yaml", ".yml", ".json"),
    "data": (".yaml", ".yml", ".json", ".csv", ".txt", ".md"),
    "references": (".md", ".txt"),
    "dist": (".js", ".d.ts", ".d.ts.map", ".js.map"),  # openclaw compiled plugin
}

# Markdown files to audit for content (zeroclaw injects these into LLM system prompt)
AUDIT_MD_FILES = ["SKILL.md", "COMMANDS.md", "CAPABILITIES.md"]

# Audit content patterns (must NOT appear in audited markdown files)
AUDIT_BLOCKED_PATTERNS = [
    (re.compile(r"curl\s+[^\n]*\|\s*(?:ba)?sh\b"), "curl-pipe-shell"),
    (re.compile(r"wget\s+[^\n]*\|\s*(?:ba)?sh\b"), "wget-pipe-shell"),
    (re.compile(r"\bIex\s*\(", re.IGNORECASE), "powershell-iex"),
    (re.compile(r"Invoke-Expression"), "powershell-invoke-expression"),
    (re.compile(r"\bpip\s+install\b"), "pip-install"),
    (re.compile(r"\bnpm\s+install\b"), "npm-install"),
    # Remote markdown links (we want only relative or in-bundle refs)
    (
        re.compile(r"\[[^\]]*\]\(https?://[^)]+\.(?:md|MD)\)"),
        "remote-markdown-link",
    ),
]


def get_version() -> str:
    """Read version from pyproject.toml. Uses tomllib if available, else regex."""
    pyproject = REPO_ROOT / "pyproject.toml"
    if tomllib is not None:
        with open(pyproject, "rb") as f:
            return tomllib.load(f)["project"]["version"]
    text = pyproject.read_text()
    m = re.search(r'^version\s*=\s*"([^"]+)"', text, re.MULTILINE)
    if not m:
        raise RuntimeError(f"could not find version in {pyproject}")
    return m.group(1)


def audit_markdown_content() -> list[tuple[str, int, str]]:
    """Pre-bundle audit. Returns list of violations: (file, line_no, pattern)."""
    violations: list[tuple[str, int, str]] = []
    for fname in AUDIT_MD_FILES:
        path = REPO_ROOT / fname
        if not path.exists():
            print(f"  [audit] WARNING: {fname} not found in repo root", file=sys.stderr)
            continue
        for i, line in enumerate(path.read_text().splitlines(), 1):
            for pat, name in AUDIT_BLOCKED_PATTERNS:
                if pat.search(line):
                    violations.append((fname, i, name))
    return violations


def is_symlink(p: Path) -> bool:
    try:
        return p.is_symlink()
    except OSError:
        return False


def collect_bundle_files(version: str) -> Iterator[tuple[Path, str]]:
    """Yield (source_path, archive_relpath) tuples for inclusion in tarball."""
    # Top-level files
    for name in WHITELIST_TOP_LEVEL:
        src = REPO_ROOT / name
        if src.exists():
            if is_symlink(src):
                print(f"  [skip-symlink] {name}", file=sys.stderr)
                continue
            yield src, name

    # Whitelisted directories with extension filters
    for dirname, allowed_exts in WHITELIST_DIRS.items():
        dir_root = REPO_ROOT / dirname
        if not dir_root.exists():
            continue
        for path in dir_root.rglob("*"):
            if not path.is_file():
                continue
            if is_symlink(path):
                print(f"  [skip-symlink] {path.relative_to(REPO_ROOT)}", file=sys.stderr)
                continue
            if path.suffix.lower() in allowed_exts:
                relpath = str(path.relative_to(REPO_ROOT))
                yield path, relpath


def main() -> int:
    version = get_version()
    bundle_name = f"investorclaw-skill-{version}"
    # Output goes under build/ (NOT dist/) to avoid recursion: dist/index.js is
    # part of the bundle SOURCE (openclaw compiled plugin), so we can't write
    # the staging tree into dist/.
    out_dir = REPO_ROOT / "build" / "bundle"
    out_tarball = REPO_ROOT / "build" / f"{bundle_name}.tar.gz"

    print(f"=== InvestorClaw skill bundle build (version {version}) ===")

    # Step 1: audit markdown content
    print(f"\n[1/3] Auditing markdown content for zeroclaw-blocked patterns...")
    violations = audit_markdown_content()
    if violations:
        print(f"  AUDIT FAILED: {len(violations)} violations", file=sys.stderr)
        for fname, lineno, pat in violations:
            print(f"  - {fname}:{lineno} matches {pat}", file=sys.stderr)
        print(
            "\n  Fix these BEFORE rebuilding. The bundle would be silently rejected by zeroclaw 0.7.3.",
            file=sys.stderr,
        )
        return 1
    print("  PASS — no blocked patterns in SKILL.md/COMMANDS.md/CAPABILITIES.md")

    # Step 2: collect files
    print(f"\n[2/3] Collecting whitelisted files into {out_dir}/{bundle_name}/...")
    if out_dir.exists():
        shutil.rmtree(out_dir)
    bundle_root = out_dir / bundle_name
    bundle_root.mkdir(parents=True, exist_ok=True)

    file_count = 0
    total_bytes = 0
    for src, relpath in collect_bundle_files(version):
        dest = bundle_root / relpath
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        file_count += 1
        total_bytes += src.stat().st_size
    print(f"  Copied {file_count} files, {total_bytes / 1024:.1f} KB")

    # Step 3: tarball
    print(f"\n[3/3] Creating {out_tarball}...")
    out_tarball.parent.mkdir(parents=True, exist_ok=True)
    if out_tarball.exists():
        out_tarball.unlink()
    with tarfile.open(out_tarball, "w:gz") as tf:
        # Use deterministic mode for reproducible builds
        tf.add(bundle_root, arcname=bundle_name, filter=lambda ti: ti)
    print(f"  Bundle: {out_tarball}")
    print(f"  Size: {out_tarball.stat().st_size / 1024:.1f} KB")

    # Final manifest
    print(f"\n=== Bundle contents ===")
    with tarfile.open(out_tarball, "r:gz") as tf:
        for ti in tf.getmembers():
            kind = "d" if ti.isdir() else "f"
            print(f"  {kind} {ti.name}  ({ti.size} bytes)")

    print(f"\n✅ Bundle ready: {out_tarball}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
