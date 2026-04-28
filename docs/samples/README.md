# portfolios/

Place your portfolio CSV or Excel files here, or set `INVESTOR_CLAW_PORTFOLIO_DIR` to point elsewhere.

## sample_portfolio.csv

A minimal anonymized sample with equities, ETFs, a bond, and cash. Use it to verify your install:

```bash
INVESTOR_CLAW_PORTFOLIO_DIR=~/Projects/InvestorClaw/portfolios \
  python3 ~/Projects/InvestorClaw/investorclaw.py holdings
```

## Supported formats

See the Portfolio File Format section in README.md for full column name reference and broker-specific notes.
