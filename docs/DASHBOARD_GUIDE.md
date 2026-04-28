# InvestorClaw Dashboard Guide

**The 15-Tab Portfolio Workstation**

The dashboard is your unified interface for portfolio analysis. All data updates in real-time as you change risk profiles or explore scenarios.

---

## Launching the Dashboard

```
/investorclaw:ic-dashboard
```

Claude Code renders a self-contained HTML workstation with:
- **15 interactive tabs**
- **Plotly charts** (risk vs. return, bond ladders, attribution)
- **Dense data tables** (positions, trades, ratings)
- **Star Trek Bloomberg Terminal design** (futuristic cyan/teal, glowing micro-interactions)

---

## Tab Guide

### CORE PORTFOLIO (5 tabs)

#### 1. Holdings
**What you own and how concentrated you are.**

- **Allocation pie chart** — equity/bond/cash breakdown by asset class
- **Sector breakdown** — weight (%) per sector (tech, healthcare, finance, etc.)
- **Top holdings table** — symbol, shares, cost basis, current value, unrealized gain/loss, % of portfolio
- **Concentration metrics** — top 10 holdings, diversification index

**Use this when:**
- Client asks "What do I own?"
- You need to explain concentration risk
- Advisors ask for a snapshot before the meeting

---

#### 2. Performance
**How you're doing vs. benchmarks.**

- **Returns card** — YTD return, 1-year, 3-year, 5-year annualized
- **Risk metrics** — volatility (annualized), max drawdown, Sharpe ratio, Sortino ratio
- **Performance chart** — cumulative returns over time (line chart)
- **Return attribution** — gains from price appreciation vs. dividends vs. rebalancing
- **Performance table** — per-ticker returns, correlation with S&P 500

**Use this when:**
- Client asks "How am I doing?"
- You need to assess risk-adjusted returns
- Portfolio needs rebalancing due to performance drift

---

#### 3. Bonds
**Fixed income analysis for your bond holdings.**

- **Bond ladder chart** — market value by maturity year (e.g., $50k due 2025, $75k due 2026)
- **Summary cards** — total bond value, weighted average duration, weighted average coupon
- **Bond table** — ticker, coupon, maturity, YTM, duration, credit quality (rating), price
- **Ladder analysis** — identify concentration in specific maturity buckets

**Use this when:**
- Client asks "When do my bonds mature?"
- You need to ladder bonds for predictable cash flow
- Rate environment changes and you want to reposition

---

#### 4. Analyst
**Wall Street consensus on your holdings.**

- **Analyst ratings table** — ticker, rating (buy/hold/sell), price target, upside/downside %, consensus
- **Consensus distribution** — pie chart of buy/hold/sell split across your holdings
- **Recommendation metrics** — average price target, % of holdings rated buy, analyst coverage count
- **Outlier analysis** — which holdings have bears or bulls; largest spread in ratings

**Use this when:**
- You want to check Wall Street's view on your holdings
- Client asks "Are analysts bullish on my stocks?"
- You're considering trimming a position with a negative consensus

---

#### 5. News
**Recent news and sentiment for your holdings.**

- **Sentiment timeline** — line chart of sentiment score over 30/60/90 days
- **Headlines** — recent news, sorted by publish date, with sentiment tags (bullish/neutral/bearish)
- **Sentiment summary** — overall tone across your portfolio
- **News correlation** — which holdings are most impacted by market news

**Use this when:**
- You want to stay on top of portfolio news
- Client mentions "I saw something about my stocks on the news"
- Sentiment is turning negative and you want to assess why

---

### ANALYSIS & OPTIMIZATION (7 tabs)

#### 6. Cashflow
**Dividend and coupon calendar for predictable income.**

- **Upcoming payments calendar** — when dividends/coupons are paid (next 12 months)
- **Payment schedule** — ticker, payment amount, payment date, yield contribution
- **Annual income projection** — expected dividend income vs. coupon payments
- **Reinvestment options** — suggestions for reinvesting or rebalancing with income

**Use this when:**
- Planning for near-term cash needs
- You want to maximize dividend income
- Client is in retirement and needs to plan withdrawals

---

#### 7. Optimize
**Rebalancing analysis and risk-adjusted allocation.**

- **Efficient frontier chart** — scatter plot of risk (x-axis) vs. return (y-axis) for current and optimized portfolios
- **Rebalancing trades** — sell overweight / buy underweight positions to reach target allocation
- **Tax impact** — estimated capital gains from rebalancing (before/after tax)
- **Optimization metrics** — Sharpe ratio improvement, expected return, standard deviation

**Use this when:**
- Portfolio has drifted from target allocation
- You want to improve risk-adjusted returns
- Tax-loss harvesting opportunities exist

---

#### 8. Synthesis
**Multi-factor analysis: combined view of all portfolio dimensions.**

- **Advisor's brief** — natural language summary synthesizing holdings, performance, risks, and opportunities
- **Key insights** — bullet points of notable findings (e.g., "Tech is 45% of portfolio, up from 40% YoY")
- **Risk assessment** — concentration risk, sector risk, geographic risk, currency risk (if applicable)
- **Opportunities** — rebalancing ideas, tax-loss harvesting, underweight sectors

**Use this when:**
- You need a quick brief before a client meeting
- You want a holistic view of the portfolio
- You're preparing quarterly review talking points

---

#### 9. What Changed
**Attribution analysis: which factors drove returns?**

- **Attribution waterfall chart** — visual breakdown of return by factor (stock selection, sector allocation, timing, etc.)
- **Factor breakdown table** — ROI from each holding, sector rotation impact, duration impact (for bonds)
- **Top movers** — best and worst performers, relative to peers
- **Portfolio drift** — deviation from target allocation over time

**Use this when:**
- Client asks "Why did I make (or lose) money?"
- You need to explain performance drivers to a client
- You're assessing manager performance or strategy effectiveness

---

#### 10. Tax Report
**Tax planning and reporting tools.**

- **Tax summary cards** — long-term capital gains, short-term gains, unrealized gains, loss-harvesting opportunities
- **Trade list** — detailed record of all realized trades (cost basis, proceeds, gains/losses, holding period)
- **Wash sale flags** — warning if recent sales would trigger wash sales if repurchased within 30 days
- **Export for accountant** — CSV with all tax-relevant data

**Use this when:**
- Tax season arrives and you need to report gains/losses
- You're considering a sale and want to know the tax impact
- You want to identify tax-loss harvesting opportunities

---

#### 11. Scenarios
**Stress testing: portfolio resilience under various market conditions.**

- **Scenario list** — predefined scenarios (equity crash -20%, rates +2%, stagflation, sector rotation)
- **Scenario outcomes chart** — bar chart showing portfolio impact under each scenario
- **Resilience metrics** — worst-case loss, best-case gain, recovery time
- **Custom scenario builder** — define your own market shock (e.g., tech -30%, rates +3%)

**Use this when:**
- Market is volatile and client is nervous
- You want to show portfolio resilience under adverse conditions
- You're setting expectations during onboarding

---

#### 12. Peer Analysis
**Factor exposure: how your portfolio compares to benchmarks and peers.**

- **Beta matrix heatmap** — correlation of your portfolio vs. different benchmarks (S&P 500, Russell 2000, etc.)
- **Active share** — % of portfolio allocation that differs from benchmark (high = active, low = passive)
- **Style drift** — tracking error vs. intended strategy (e.g., "intended value, but now 40% growth")
- **Factor exposure** — exposure to factors (value, growth, momentum, dividend yield, quality)

**Use this when:**
- You want to assess active vs. passive positioning
- Client asks "How am I different from a low-cost index?"
- You're reviewing strategy alignment with stated objectives

---

### REPORTS & CONFIGURATION (3 tabs)

#### 13. Reports
**Export and sharing tools.**

- **Export buttons** — CSV, JSON, PDF (all positions and analysis)
- **Report templates** — one-page summary, detailed analysis, tax report, advisor handoff
- **Email-ready formats** — HTML summary for client email, printable PDF
- **Audit trail** — fingerprint (SHA-256 hash) for reproducibility and verification

**Use this when:**
- Client requests a report for their records
- You need to share with a CPA or tax advisor
- You're archiving a quarterly review

---

#### 14. Settings
**Configuration and preferences.**

- **Provider selection** — data source (yfinance, Finnhub, Polygon, etc.)
- **Risk profile** — investor risk tolerance (conservative/moderate/aggressive)
- **Guardrails** — enable educational disclaimers, tax optimization alerts, concentration warnings
- **Stonkmode toggle** — enable humorous market narration mode (30 fictional finance personalities)
- **Advanced options** — benchmarks, rebalancing frequency, tax lot method

**Use this when:**
- Setting up portfolio for first time
- Changing data sources (e.g., adding Finnhub for better analyst data)
- Enabling/disabling features

---

#### 15. About
**Version info and disclaimer.**

- **Version** — InvestorClaw v2.0.0 (open-source, Apache 2.0 licensed)
- **Disclaimer** — educational analysis only, not investment advice
- **Audit fingerprint** — SHA-256 hash for this analysis (reproducibility)
- **Data freshness** — timestamp of last data update
- **License** — Apache 2.0 free/open-source, dual enterprise tier available

---

## Keyboard Navigation

- **Tab key** — switch between tabs (left/right arrows also work)
- **Enter/Space** — select active tab
- **Focus states** — cyan glow indicates focused element

## Exporting Data

**CSV Export**
- All positions, with cost basis, current value, gain/loss
- All analysis tables
- Import into Excel or other tools

**JSON Export**
- Full dashboard data structure
- Programmatic analysis possible
- API-ready format

**PDF Report**
- Print-to-PDF from browser (Cmd+P / Ctrl+P)
- Includes charts, tables, summary
- Client-ready format

---

## Design Notes

**Star Trek Bloomberg Terminal Aesthetic**
- **Colors**: Electric cyan (#00d9ff), teal (#00ffcc) on space-black backgrounds
- **Typography**: Courier Prime (technical), Michroma (futuristic headers)
- **Effects**: Glowing borders on hover, subtle scanlines, text shadows (sci-fi feel)
- **Density**: Bloomberg-style information-rich layout with clear visual hierarchy

**Responsive**
- Works on desktop, tablet, mobile
- Tables scroll horizontally on narrow screens
- Charts scale responsively

---

## Tips & Tricks

### Quick Analysis
1. Launch dashboard
2. Glance at **Holdings** tab (what's concentrated?)
3. Check **Synthesis** tab (advisor brief)
4. Explore **Optimize** tab if rebalancing needed

### Client Presentations
1. Share **Dashboard URL** or screenshot
2. Walk through **Synthesis** for talking points
3. Show **Performance** if doing well, **What Changed** if explaining shortfalls
4. Discuss **Tax Report** ahead of year-end planning
5. Export **PDF** for client file

### Tax Planning
1. Open **Tax Report** tab
2. Identify wash-sale risks
3. Review unrealized gains/losses
4. Plan tax-loss harvesting in **Optimize** tab
5. Export **CSV** for accountant

### Stress Testing
1. Open **Scenarios** tab
2. Review impact under bear market, rate spike, etc.
3. Use results to set client expectations
4. Document in **Reports** export

---

## Troubleshooting

### Dashboard Takes Long to Load
- **First run**: Data fetching is normal (10-30 seconds)
- **Subsequent runs**: Uses cached data (faster)
- **Large portfolio**: 200+ holdings may take longer

### Charts Not Rendering
- Check browser console (F12) for errors
- Ensure Plotly CDN is accessible (https://cdn.plot.ly)
- Reload page (Cmd+R / Ctrl+R)

### Missing Data in Tabs
- Not all data sources are required
- "No data" message is normal for optional tabs (e.g., if no bonds)
- Run full `/investorclaw:ic-dashboard` to fetch all available data

### Export Not Working
- Try different format (CSV vs. JSON)
- Check browser permissions
- Use Print-to-PDF as fallback

---

## More Information

- **Commands**: See `/investorclaw:ic-help` for all 22 commands
- **Architecture**: See `../docs/ARCHITECTURE.md`
- **Data Privacy**: See `../docs/DATA_FLOW.md`
- **Financial Terminology**: See `../docs/FINANCIAL_TERMINOLOGY.md`

