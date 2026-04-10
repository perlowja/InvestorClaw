#!/usr/bin/env python3
"""
Path resolution utilities for InvestorClaw.

Finds portfolio files and report directories based on environment and conventions.
"""

import os
from pathlib import Path
from typing import Optional


def get_portfolio_dir(skill_dir: Path) -> Path:
    """
    Get the portfolio directory (configurable via env var or default).

    Returns Path to portfolio directory.
    """
    _port_env = os.environ.get("INVESTOR_CLAW_PORTFOLIO_DIR", "").strip()
    if _port_env:
        return Path(_port_env).expanduser()
    return skill_dir / "portfolios"


def get_reports_dir() -> Path:
    """
    Get the reports output directory (configurable via env var or default).

    Returns Path to reports directory (creates if doesn't exist).
    """
    _reports_env = os.environ.get("INVESTOR_CLAW_REPORTS_DIR", "").strip()
    if _reports_env:
        reports_dir = Path(_reports_env).expanduser()
    else:
        reports_dir = Path.home() / "portfolio_reports"

    # Ensure it exists
    reports_dir.mkdir(parents=True, exist_ok=True)
    return reports_dir


def find_portfolio_file(skill_dir: Path) -> Optional[str]:
    """
    Find the best portfolio file to use.

    Priority:
    1. master_portfolio.csv (consolidation output)
    2. Most recently modified *_extracted.csv
    3. Most recently modified *.csv file

    Returns path string, or None if no file found.
    """
    portfolio_dir = get_portfolio_dir(skill_dir)

    # First choice: master_portfolio.csv (consolidation output)
    master = portfolio_dir / "master_portfolio.csv"
    if master.exists():
        return str(master)

    # Second choice: any *_extracted.csv file (but not bonds)
    extracted_files = list(portfolio_dir.glob("*_extracted.csv"))
    extracted_files = [f for f in extracted_files if "_bonds" not in f.name]
    if extracted_files:
        latest = max(extracted_files, key=lambda p: p.stat().st_mtime)
        return str(latest)

    # Third choice: any raw *.csv file (e.g., directly placed broker exports)
    raw_csv_files = [
        f for f in portfolio_dir.glob("*.csv")
        if not f.name.startswith('.') and "_bonds" not in f.name
    ]
    if raw_csv_files:
        latest = max(raw_csv_files, key=lambda p: p.stat().st_mtime)
        return str(latest)

    # Fallback: return None
    return None
