# InvestorClaw Quick Start (5 minutes)

**Get portfolio analysis in 5 minutes. No setup required.**

---

## Step 1: Install (1 minute)

In Claude Code, run:

```
/plugin marketplace add https://gitlab.com/argonautsystems/InvestorClaude.git
/plugin install investorclaw@investorclaude
```

Claude handles everything automatically. No manual setup needed.

---

## Step 2: Load Your Portfolio (2 minutes)

Choose one:

### Option A: Upload CSV
```
Analyze my portfolio
[Schwab_positions.csv attached]
```
Claude extracts holdings automatically.

### Option B: Screenshot
```
Here's my broker's positions page
[screenshot.png attached]
```
Claude extracts holdings via vision.

### Option C: Use Setup Wizard
```
/investorclaw:ic-setup
```
Interactive guide for your broker format.

---

## Step 3: View Dashboard (2 minutes)

```
/investorclaw:ic-dashboard
```

Explore the 15-tab workstation:
1. **Holdings** — what you own
2. **Performance** — how you're doing
3. **Bonds** — bond analysis (if you have bonds)
4. **Analyst** — Wall Street consensus
5. **News** — recent headlines
6. **Synthesis** — advisor brief (one-page summary)
7. Plus 8 more for deep analysis

Click tabs. Ask Claude questions: "Why is tech so concentrated?"

---

## Common Questions

**Q: Do I need API keys?**
A: No. Works out-of-the-box with free data. Optional keys (Finnhub, NewsAPI) improve data quality.

**Q: Can I see the dashboard in Claude Code?**
A: Yes! `/investorclaw:ic-dashboard` renders inline. Also available as standalone HTML file.

**Q: How do I export my portfolio?**
A: Click "Reports" tab → Export CSV/JSON. Or use `/investorclaw:ic-report`.

**Q: Is this financial advice?**
A: No. Educational analysis only. Claude includes disclaimers throughout.

**Q: What if my broker format isn't supported?**
A: InvestorClaw handles CSV/XLS/XLSX/PDF from most brokers (Schwab, Fidelity, Vanguard, UBS, etc.). If unsure, attach your file and Claude will auto-detect.

---

## Next Steps

### For Personal Use
1. Run `/investorclaw:ic-dashboard` monthly
2. Check **Synthesis** tab for changes
3. Export **Reports** for your records

### For Advisor Use
1. Have client upload portfolio
2. Share dashboard screenshot/PDF with client
3. Use **Synthesis** for talking points
4. Export **Tax Report** for year-end planning

### For Deep Analysis
- Use individual commands: `/investorclaw:ic-holdings`, `/investorclaw:ic-performance`, etc.
- See all 24 commands: `/investorclaw:ic-help`
- Full guide: [DASHBOARD_GUIDE.md](DASHBOARD_GUIDE.md)

---

## Documentation

- **Dashboard Guide**: [DASHBOARD_GUIDE.md](DASHBOARD_GUIDE.md) — detailed tab guide + tips
- **All Commands**: `/investorclaw:ic-help` or [COMMAND_INDEX.md](COMMAND_INDEX.md)
- **Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **Data Privacy**: [SECURITY.md](SECURITY.md)

---

**That's it! You're ready to analyze your portfolio.** 🚀

