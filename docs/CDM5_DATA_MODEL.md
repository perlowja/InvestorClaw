# CDM 5 Data Model — InvestorClaw Architecture

**Status**: Production  
**Standard**: FINOS Common Data Model 5.0  
**Purpose**: Unified portfolio representation across all asset classes

---

## Overview

InvestorClaw uses FINOS CDM 5 as its canonical data model. CDM 5 is the financial industry standard for representing securities, derivatives, and complex financial instruments. This ensures compatibility with institutional infrastructure (DTCC, SEC, major banks) and enables sophisticated analytics across asset classes without vendor lock-in.

---

## Top-Level Portfolio Structure

```
portfolio (CDM 5.x)
├── cdmVersion: "5.0.0"
├── metadata
│   ├── asOfDate: "2026-04-17"
│   ├── portfolioName: "Multi-Strategy Growth"
│   ├── currency: "USD"
│   ├── reportingEntity: "Jason Perlow"
│   └── riskProfile: "balanced"
│
├── summary
│   ├── totalValue: 100000000.00
│   ├── totalReturn: 0.0537  # 5.37% YTD
│   ├── sharpeRatio: 0.72
│   ├── position_count: {
│   │   "equity": 142,
│   │   "bond": 38,
│   │   "crypto": 8,
│   │   "metals": 6,
│   │   "futures": 3,
│   │   "cash": 2
│   │ }
│   ├── allocation: {
│   │   "equity": 0.58,
│   │   "bond": 0.28,
│   │   "cash": 0.08,
│   │   "crypto": 0.04,
│   │   "alternative": 0.02
│   │ }
│   └── sector_breakdown: {
│   │   "Technology": 0.22,
│   │   "Healthcare": 0.15,
│   │   "Financials": 0.12,
│   │   ...
│   │ }
│
├── accounts [array of account containers]
│   └── account[0]
│       ├── accountId: "brkx-12345"
│       ├── accountName: "Primary Brokerage"
│       ├── accountType: "Individual"
│       ├── custodian: "Fidelity"
│       ├── accountValue: 45000000.00
│       └── positions [array]
│
└── portfolioState
    ├── equity [array of equity holdings]
    ├── fixed_income [array of bonds]
    ├── crypto [array of crypto positions]
    ├── metals [array of precious metals]
    ├── futures [array of derivatives]
    └── cash
```

---

## Asset Type Schemas

### EQUITY Position

```json
{
  "positionId": "AAPL-001-45000",
  "assetType": "equity",
  "symbol": "AAPL",
  "name": "Apple Inc.",
  "quantity": 45000,
  "currentPrice": 175.32,
  "marketValue": 7889400.00,
  "cost_basis": 7100000.00,
  "unrealizedGain": 789400.00,
  "unrealizedGainPct": 0.1112,
  "acquisition_date": "2021-06-15",
  "accountId": "brkx-12345",
  "cdm5_fields": {
    "product": {
      "contractualProduct": {
        "economicTerms": {
          "payout": "EquityPayout",
          "underlyingAsset": {
            "identifier": "ISIN:US0378331005",
            "ticker": "AAPL"
          }
        }
      }
    },
    "sector": "Technology",
    "marketCap": "2.8T",
    "peRatio": 28.5,
    "yieldPct": 0.0042
  }
}
```

### BOND Position (Fixed Income)

```json
{
  "positionId": "MUNI-CA-2051-100",
  "assetType": "bond",
  "bondType": "municipal",
  "issuer": "California State",
  "cusip": "13026565AN",
  "quantity": 100,
  "currentPrice": 102.50,
  "marketValue": 10250000.00,
  "cost_basis": 10000000.00,
  "unrealizedGain": 250000.00,
  "unrealizedGainPct": 0.025,
  "acquisition_date": "2024-03-20",
  "accountId": "brkx-12345",
  "cdm5_fields": {
    "product": {
      "contractualProduct": {
        "economicTerms": {
          "payout": "FixedRatePayout",
          "coupon": {
            "rate": 0.045,
            "frequency": "SEMI_ANNUAL",
            "nextPaymentDate": "2026-06-01"
          }
        }
      }
    },
    "maturityDate": "2051-06-01",
    "duration": 4.8,
    "convexity": 28.3,
    "ytm": 0.032,
    "creditRating": "AA",
    "taxStatus": "tax-exempt"
  }
}
```

### CRYPTO Position

```json
{
  "positionId": "BTC-USD-0050",
  "assetType": "crypto",
  "symbol": "BTC-USD",
  "name": "Bitcoin",
  "quantity": 0.50,
  "currentPrice": 42500.00,
  "marketValue": 21250000.00,
  "cost_basis": 18750000.00,
  "unrealizedGain": 2500000.00,
  "unrealizedGainPct": 0.1333,
  "acquisition_date": "2023-11-08",
  "accountId": "kraken-001",
  "cdm5_fields": {
    "product": {
      "contractualProduct": {
        "economicTerms": {
          "payout": "CryptoPayout",
          "cryptoAsset": {
            "identifier": "BTC",
            "blockchain": "Bitcoin",
            "addressType": "p2wpkh"
          }
        }
      }
    },
    "blockchain": "Bitcoin",
    "priceSource": "yfinance",
    "vol24h": 2500000000.00,
    "marketCapRank": 1
  }
}
```

### METALS Position

```json
{
  "positionId": "GLD-001-5000",
  "assetType": "metals",
  "symbol": "GLD",
  "name": "SPDR Gold Shares ETF Trust",
  "quantity": 5000,
  "currentPrice": 195.30,
  "marketValue": 976500.00,
  "cost_basis": 900000.00,
  "unrealizedGain": 76500.00,
  "unrealizedGainPct": 0.085,
  "acquisition_date": "2022-08-10",
  "accountId": "brkx-12345",
  "cdm5_fields": {
    "product": {
      "contractualProduct": {
        "economicTerms": {
          "payout": "CommodityPayout",
          "commodity": {
            "commodityType": "PRECIOUS_METALS",
            "metalType": "GOLD"
          }
        }
      }
    },
    "metal_type": "gold",
    "spotPrice": 2050.00,
    "priceSource": "yfinance"
  }
}
```

### FUTURES Position

```json
{
  "positionId": "ES-H26-50",
  "assetType": "futures",
  "symbol": "/ESH26",
  "name": "E-mini S&P 500 March 2026",
  "quantity": 50,
  "currentPrice": 5285.50,
  "marketValue": 13213750.00,
  "cost_basis": 12875000.00,
  "unrealizedGain": 338750.00,
  "unrealizedGainPct": 0.0263,
  "acquisition_date": "2026-02-01",
  "accountId": "td-futures-001",
  "cdm5_fields": {
    "product": {
      "contractualProduct": {
        "economicTerms": {
          "payout": "InterestRatePayout",
          "underlying": {
            "identifier": "SPX",
            "priceType": "SPOT"
          }
        }
      }
    },
    "contract_symbol": "ESH26",
    "expiry_date": "2026-03-20",
    "contract_size": 250,
    "notional_value": 13213750.00,
    "margin_requirement": 660000.00,
    "exchangeCode": "GLOBEX",
    "priceSource": "yfinance"
  }
}
```

---

## Why CDM 5?

### 1. Financial Semantics
Each asset type declares its payout structure (EquityPayout, FixedRatePayout, CryptoPayout, CommodityPayout). This enables automatic risk calculation, dividend projection, coupon estimation.

### 2. Standardization
- Same structure for all asset classes (equity, bond, crypto, metals, futures, options)
- SEC, DTCC, major clearing houses mandate CDM 5 for reporting by 2028
- No vendor lock-in to proprietary formats

### 3. Composability
Nested `product.contractualProduct.economicTerms` allows "stacking" of complex contracts (bonds with embedded callables, crypto with lending collateral, derivatives with options overlay).

### 4. Extensibility
New asset types (NFTs, real-world assets, digital commodities) just add new Payout types. Existing code reads unknown types without breaking.

### 5. Institutional Grade
- FINOS standard (Linux Foundation)
- Used by JPMorgan, Goldman Sachs, State Street, Citadel
- Future-proof as financial markets evolve

---

## Compact Summary Format (UI Layer)

For web dashboards and lightweight clients, CDM 5 is compressed:

```json
{
  "summary": {
    "totalValue": 100000000.00,
    "unrealizedGain": 5370000.00,
    "unrealizedGainPct": 0.0537,
    "position_count": {"equity": 142, "bond": 38, "crypto": 8, "metals": 6, "futures": 3, "cash": 2}
  },
  "top_equity": [
    {"symbol": "AAPL", "marketValue": 7889400, "pct": 0.079},
    {"symbol": "MSFT", "marketValue": 6750000, "pct": 0.067}
  ],
  "sector_breakdown": {"Technology": 0.22, "Healthcare": 0.15, "Financials": 0.12},
  "accounts": {
    "brkx-12345": {"value": 45000000, "name": "Primary"},
    "kraken-001": {"value": 21250000, "name": "Crypto"}
  }
}
```

---

## Command Mapping

| Command | Input | Output | Purpose |
|---------|-------|--------|---------|
| ic-holdings | CDM 5 portfolio | holdings.json + summary | Asset allocation, position counts |
| ic-bonds | CDM 5 fixed_income | performance.json | YTM, duration, ladder, tax |
| ic-analyst | CDM 5 equity | analyst.json | P/E, ratings, consensus |
| ic-performance | CDM 5 all assets | performance.json | Beta, Sharpe, attribution |
| ic-peer | CDM 5 all assets | peer.json | Factor exposure, style drift |
| ic-optimize | CDM 5 all assets | optimize.json | Efficient frontier, rebalance |
| ic-whatchanged | CDM 5 + snapshots | whatchanged.json | Attribution, factor moves |
| ic-scenario | CDM 5 all assets | scenario.json | Stress tests, VaR, repricing |
| ic-cashflow | CDM 5 bonds + equity | cashflow.json | Dividend/coupon calendar, taxes |

---

## Integration Points

### Python API
```python
from config.schema import normalize_portfolio, validate_portfolio
from services.portfolio_utils import load_holdings_list

# Load and normalize any portfolio format
data = normalize_portfolio(raw_json_or_dict)
validate_portfolio(data)

# Access by asset class
holdings = load_holdings_list(data)
equity_holdings = [h for h in holdings if h.is_equity()]
bonds = [h for h in holdings if h.is_bond()]
crypto = [h for h in holdings if h.is_crypto()]
```

### JSON Files
- `~/.investorclaw/portfolio_reports/.raw/holdings.json` — full CDM 5 structure
- `~/.investorclaw/portfolio_reports/holdings_summary.json` — compact summary for dashboards
- All other reports (`performance.json`, `analyst.json`, etc.) reference CDM holdings

---

## Related Documentation

- **Setup**: [`claude/README.md`](../claude/README.md) — environment variables, provider configuration
- **Stonkmode**: [`docs/STONKMODE.md`](./STONKMODE.md) — narrative personas and entertainment features
- **Commands**: [`claude/skills/investorclaw-setup/SKILL.md`](../claude/skills/investorclaw-setup/SKILL.md) — command reference
- **Bug Fixes**: [`investorclaw-setup-bugs.md`](../investorclaw-setup-bugs.md) — open issues and roadmap
