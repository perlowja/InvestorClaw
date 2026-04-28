# Table Rendering Guide for InvestorClaw Commands

**Status**: Pattern established | Utility module available  
**Updated**: 2026-04-16

---

## Overview

Commands in InvestorClaw should detect when running in an interactive terminal (Claude Code, bash, etc.) and render formatted tables with ANSI colors instead of dumping raw JSON to stdout.

**Key principle**: JSON to files (for downstream scripts), formatted tables to interactive terminals.

---

## When to Render Tables

Render formatted tables when:
- Output goes to **interactive terminal** (TTY, not piped)
- Running in **Claude Code** (CLAUDE_CODE env var set)
- User is **reading the output** (not feeding it to another script)

Write JSON to files only:
- Keep JSON output files for downstream tools
- Never dump JSON to stdout in interactive mode (causes truncation)

---

## Implementation Pattern

### 1. Detect Interactive Mode

```python
from rendering.interactive_output import is_interactive

if is_interactive():
    # Render formatted table for human reading
    print_formatted_output(data)
else:
    # Output JSON for scripts
    print(json.dumps(data))
```

### 2. Use Formatting Helpers

```python
from rendering.interactive_output import (
    Colors, format_currency, format_percent,
    format_header, print_summary
)

# Header with ANSI formatting
print(format_header("Portfolio Summary"))

# Currency with color (green for gains, red for losses)
print(f"Gain: {format_currency(5234.50)}")

# Percentage with color
print(f"Return: {format_percent(3.75)}")

# Summary section with labels
print_summary("Allocation", {
    "stocks": 1_250_000,
    "bonds": 500_000,
    "cash": 50_000,
}, labels={
    "stocks": "Equities",
    "bonds": "Fixed Income",
    "cash": "Cash & Equivalents",
})
```

### 3. Reference Implementations

- **portfolio_analyzer.py** — Complete example with tables, alerts, colors
- **fixed_income_analysis.py** — Includes summary output and recommendations
- **analyze_performance_polars.py** — Uses ANSI for portfolio summaries

---

## Color Reference

```python
Colors.RED      # Losses, errors, critical alerts
Colors.GREEN    # Gains, success, positive metrics
Colors.YELLOW   # Warnings, medium priority items
Colors.CYAN     # Headers, ticker symbols
Colors.WHITE    # Values, prices, important numbers
Colors.GREY     # Separators, metadata, less important text
```

### Usage Examples

```python
from rendering.interactive_output import Colors, format_currency

# Red for negative change
print(f"{Colors.RED}-$2,345.50{Colors.RESET}")

# Green for positive change
print(f"{Colors.GREEN}+$1,234.25{Colors.RESET}")

# Cyan for ticker
print(f"{Colors.CYAN}AAPL{Colors.RESET}")

# Helper for automatic color selection
print(f"Change: {format_currency(value)}")  # Auto red/green
```

---

## Commands Needing Updates

Priority order for adding table rendering:

### High Priority (Critical Commands)
1. **ic-holdings** — Currently dumps JSON, should show portfolio snapshot
2. **ic-bonds** — Bond summary table
3. **ic-analyst** — Analyst ratings and consensus

### Medium Priority
4. **ic-news** — News sentiment summary
5. **ic-lookup** — Single ticker detail card

### Low Priority
6. **ic-report** — Just shows file paths (OK, but could show summary)

---

## Testing

To test interactive detection:

```bash
# Test interactive (should show table)
python3 commands/ic_holdings.py ~/portfolio_reports/holdings.json

# Test piped (should output JSON)
python3 commands/ic_holdings.py ~/portfolio_reports/holdings.json | jq .
```

---

## Future: Artifact Generation

Once table rendering is working, consider:
- Generate HTML artifacts for Claude Code artifact viewer
- Produce CSV tables for easy copy-paste
- Integrate with `/ic-dashboard` for unified output

---

## Questions?

See `rendering/interactive_output.py` for all available helpers and color codes.
