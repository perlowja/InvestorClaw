# InvestorClaw — Features & Capabilities

**v2.1.4** | What InvestorClaw does and what it doesn't

---

## What It Does ✅

### Portfolio Analysis (Deterministic Pipelines)

All financial calculations run in sealed Python subprocesses — **the LLM never touches portfolio math**:

- **Holdings snapshot**: Live prices (Finnhub/Massive/Alpha Vantage/yfinance), concentration ratios, sector/asset-class breakdown
- **Performance analysis**: Sharpe ratio, beta, max drawdown, volatility, dividend yield, correlation matrix
- **Bond analytics**: YTM (using Newton-Raphson), Macaulay & modified duration, convexity, FRED Treasury benchmarks
- **Concentration metrics**: Herfindahl-Hirschman index, sector concentration risk, diversification classification
- **News correlation**: Portfolio news aggregation with sentiment tagging (yfinance/NewsAPI)
- **Analyst consensus**: Real-time analyst ratings and price targets (Finnhub)
- **Portfolio optimization**: Modern Portfolio Theory — Sharpe ratio maximization, min-volatility, Black-Litterman model, discrete allocation, efficient frontier visualization

### LLM Synthesis (Read-Only)

The operational LLM receives **serialized summaries only** (compact, hand-crafted JSON):

- Multi-factor portfolio analysis with key insights
- Holdings recommendations (based on concentration/diversification analysis)
- Risk assessment and suitability caveats
- Discussion talking points for advisor conversations

The LLM **reads results, surfaces indicators, contextualizes findings**. It does not:
- Perform math
- Make fiduciary recommendations
- Assess personal suitability
- Replace a human financial advisor

### Guardrails (Always-On)

Built-in constraints enforced at the agent level:

- ✅ Educational-only mode (no "buy/sell now" recommendations)
- ✅ Suitability caveats (adds disclaimers about personal context)
- ✅ FA Professional mode (different language for advisors vs. retail)
- ✅ Synthetic output detection (HMAC fingerprints verify consultation results)
- ✅ Data privacy (no logging of personal account details)

### Configuration & Deployment

- **Zero-config fallback**: No API keys? Uses `yfinance` (free, unlimited)
- **Flexible backends**: Local (Ollama/llama-server) or cloud (Together.ai, xAI, OpenAI, Google)
- **Environment precedence**: Shell overrides → Setup wizard config → `.env` defaults
- **Automatic updates**: Checks GitLab/GitHub on startup, offers one-click install
- **Dual deployment**: Single-investor (personal) or FA Professional (advisor) modes

---

## What It Doesn't Do ❌

### Not a Trading Platform

- ❌ Does not execute trades
- ❌ Does not replace your broker's portal
- ❌ Does not manage accounts or transfer funds
- ❌ Does not integrate with brokerage APIs for execution

### Not a Robo-Advisor

- ❌ Does not manage your money
- ❌ Does not rebalance automatically
- ❌ Does not assess personal risk tolerance
- ❌ Does not make suitability determinations
- ❌ Does not issue fiduciary advice

### Not Financial Advice

- ❌ Does not tell you what to buy/sell
- ❌ Does not promise returns or minimize risk
- ❌ Does not personalize recommendations based on your financial situation
- ❌ Results are educational, not investment advice

### Not Real-Time

- ❌ Portfolio data is T+1 or cached (not tick-by-tick)
- ❌ Market data refreshes on command, not continuously
- ❌ News feed is historical, not streaming

---

## Key Strengths

1. **Computational Integrity**
   - All math is deterministic, verifiable Python code
   - No black-box LLM calculations
   - Reproducible results

2. **Context Window Efficiency**
   - Compact serialized output (270 positions fit in ~2K tokens)
   - Allows long conversation histories in OpenClaw

3. **Privacy-First**
   - No data sent to cloud unless configured
   - Can run fully locally (air-gapped)
   - HMAC fingerprints verify synthesis integrity

4. **Flexible Backends**
   - Works with zero API keys
   - Cloud or local LLM (optional, not required)
   - Graceful degradation if services unavailable

5. **Guardrails Built-In**
   - Educational-only mode enforced
   - Suitability caveats automatic
   - Governance tools for FA Professional deployments

6. **Production-Ready**
   - FINOS CDM 5.x inspired schema
   - Tested on 50–500 holding portfolios
   - Apache 2.0 licensed (open source)

---

## Technology Stack

### Data Sources

| Provider | Data | Free Tier | Fallback |
|----------|------|-----------|----------|
| **yfinance** | Prices, history, dividends | Unlimited | Primary default |
| **Finnhub** | Real-time quotes, analyst ratings | 60 req/min | Quotes + analyst |
| **Polygon/Massive** | Full OHLCV, prev-day | Premium only | Historical data |
| **Alpha Vantage** | EOD adjusted prices, earnings | 25 req/day | Supplemental |
| **FRED** | Treasury yields, TIPS | Unlimited | Bond benchmarks |
| **NewsAPI** | Portfolio news | 100 req/day | Sentiment |

### Computation

- **Polars** — High-performance dataframe (SIMD vectorization)
- **NumPy/SciPy** — Matrix math, statistics, optimization
- **PyPortfolioOpt** — Modern Portfolio Theory (Sharpe, min-vol, Black-Litterman)
- **scipy.optimize.brentq** — Root-finding for bond YTM calculations

### LLM Integration (Optional)

- **Local**: Ollama (~4K context) or llama-server (~131K context)
- **Cloud**: Together.ai, xAI, OpenAI, Google Cloud (via OpenAI-compatible APIs)

### Deployment

- **Standalone**: Python CLI wrapper (`investorclaw.py`)
- **OpenClaw Plugin**: MCP-compliant skill with guardrails

---

## Financial Metrics Explained

See [CONFIGURATION.md](CONFIGURATION.md) for full reference, or:

```bash
/portfolio holdings --verbose    # Detailed metrics with Dr. Stonk explanations
```

**Key metrics**:
- **Sharpe Ratio**: Return per unit of risk (higher is better; >2.0 is excellent)
- **Beta**: Market sensitivity (1.0 = market, >1.0 = volatile)
- **Max Drawdown**: Largest peak-to-trough decline (lower is better)
- **Duration**: Bond's effective maturity / interest rate sensitivity
- **YTM**: Bond's yield to maturity (internal rate of return)
- **HHI**: Concentration (0–10,000 scale; >2500 = highly concentrated)

All explained via **Dr. Stonk** (from the planet Hephaestus) on demand.

---

## Typical Workflow

1. **Setup** (`/portfolio setup`): Discover portfolio CSV/Excel/PDF files
2. **Analyze** (`/portfolio holdings`, `/portfolio bonds`, `/portfolio performance`): Generate reports
3. **Synthesize** (`/portfolio synthesize`): Get LLM insights + key talking points
4. **Optimize** (`/portfolio optimize sharpe`): Generate rebalancing suggestions
5. **Export** (`/portfolio report`): Save Excel report for advisor discussion
6. **Discuss**: Use outputs to have informed conversation with your FA

---

## Sample Output

### End-of-Day Report

The `/portfolio eod` command generates an HTML report with portfolio summary, performance analysis, and charts:

<p align="center">
  <img src="https://cdn.jsdelivr.net/gh/argonautsystems/InvestorClaw@main/assets/eod-report-sample.png" alt="End-of-Day Report Sample" width="800"/>
</p>

**Features**:
- Real-time holdings snapshot
- Performance metrics (Sharpe, beta, max drawdown)
- Sector allocation chart
- News sentiment timeline
- Email-ready HTML (dark theme, mobile-responsive)

---

## Stonkmode 🎪

After serious analysis, enable **Stonkmode** for entertainment:

```bash
/portfolio stonkmode on
/portfolio holdings                 # Now with 30 fictional TV finance personalities
```

Stonkmode wraps analysis in satirical commentary. It's entertainment, not advice. Its existence is the clearest signal this is **not** institutional financial software.

See [STONKMODE.md](docs/STONKMODE.md) for full details.

---

## Safety & Compliance

### Built-In Safeguards

- ✅ Educational-only guardrails (no "buy this" recommendations)
- ✅ No trade execution (can't move money)
- ✅ Suitability disclaimers (automatic caveats about personal context)
- ✅ HMAC fingerprints (verify synthesis hasn't been forged)
- ✅ Audit logs (track all commands + outputs)

### For Financial Advisors (FA Professional Mode)

- ✅ Structured output (client-ready reports)
- ✅ Professional tone (advisor language)
- ✅ Guardrail relaxation (allows qualified recommendations)
- ✅ Compliance hooks (audit trail + fingerprints)

---

## Performance Benchmarks

**Test environment**: macOS M1, 50-holding portfolio, yfinance backend

| Operation | Time | Tokens |
|-----------|------|--------|
| Holdings snapshot | ~2s | 1.2K |
| Performance analysis | ~3s | 1.8K |
| Bond analytics (10 bonds) | ~1s | 0.9K |
| Full synthesis | ~8s (with consultation) | 3.5K |
| Portfolio optimization | ~2s | 2.1K + SVG plot |

Scales linearly with holdings count. 500 holdings = ~15s end-to-end.

---

## See Also

- **Quick start**: [QUICKSTART.md](QUICKSTART.md)
- **All commands**: [COMMANDS.md](COMMANDS.md)
- **Configuration**: [CONFIGURATION.md](CONFIGURATION.md)
- **Optimization**: see [COMMANDS.md](COMMANDS.md) § "Portfolio Optimization" and `commands/optimize.py`
- **Stonkmode**: [STONKMODE.md](docs/STONKMODE.md)
- **Deployment**: [DEPLOYMENT.md](DEPLOYMENT.md)

---

**Questions?** Open an issue: https://gitlab.com/argonautsystems/InvestorClaw/-/issues
