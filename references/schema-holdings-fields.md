# Holdings Schema — Field Reference

Describes the classification fields written into `holdings_summary.json`.
The presentation rules that consume these live in
[presentation-rules.md](presentation-rules.md).

## Per-holding fields

Each holding in `holdings_summary.json` includes:

- `security_type`: `"etf"` | `"mutual_fund"` | `"equity"`
- `is_etf`: `true` | `false`
- `financial_type`: `"ira"` | `"roth_ira"` | `"401k"` | `"brokerage"` |
  `"taxable"` | `"unknown"`

## Account-level classification

Accounts are classified as:

- `"etf_bundle"` — 80%+ funds
- `"mixed"` — 30–80%
- `"individual_stocks"` — <30%

## 401K / mutual-fund handling

Funds without standard tickers use synthetic symbol IDs (e.g.,
`FID_CONTRA_POOL`). Set `proxy_symbol` to a publicly-traded equivalent for
live pricing via yfinance (e.g., `FCNTX`). Without a proxy, `purchase_price`
is used as current NAV.

Account type is inferred from the account name if not explicitly set in the
CSV:

- `ROTH` → `roth_ira`
- `IRA` → `ira`
- `401K` or `RETIREMENT` → `401k`
- `BROKERAGE` → `brokerage`

The `financial_type` field appears in the `accounts` block of `holdings.json`.

## Merging multiple portfolio files

Use the installed `investorclaw holdings` entry point or the setup flow to
load portfolio files. Multi-account consolidation is handled inside
`ic-engine`; the adapter docs should not call old in-repo implementation
scripts directly. Consolidation preserves account boundaries and deduplicates
symbol+account combinations.
