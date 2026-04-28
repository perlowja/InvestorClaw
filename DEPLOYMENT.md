# InvestorClaw Production Deployment Guide

Version: 2.1.9  
Updated: 2026-04-23  
Status: Production Ready

## Pre-deployment checklist

Complete this checklist before your first production deployment.

### Configure the environment

- [ ] Secure API keys.
- [ ] Store all keys in `.env`.
- [ ] Keep `.env` out of version control.
- [ ] Rotate all keys before the first production deploy.
- [ ] Use a secrets manager in production, such as AWS Secrets or HashiCorp Vault.

- [ ] Configure data providers.
- [ ] Configure at least one data provider. `yfinance` is the zero-config default.
- [ ] Set `FINNHUB_KEY` if you use analyst consensus features.
- [ ] Set `NEWSAPI_KEY` if you use news correlation features.
- [ ] Set `FRED_API_KEY` if you use bond yield benchmarking.

- [ ] Configure the narrative and stonkmode pipeline.
- [ ] Set `INVESTORCLAW_NARRATIVE_PROVIDER` to `ollama` or `openai_compat`.
- [ ] Configure `INVESTORCLAW_NARRATIVE_ENDPOINT`.
- [ ] Set `INVESTORCLAW_NARRATIVE_API_KEY` if you use a cloud provider.
- [ ] Set `INVESTORCLAW_NARRATIVE_MODEL`.
- [ ] Test the narration pipeline with `/portfolio holdings` and stonkmode enabled.

- [ ] Configure the consultation model if you plan to use it.
- [ ] Set `INVESTORCLAW_CONSULTATION_ENABLED` to `true` or `false`.
- [ ] Verify that `INVESTORCLAW_CONSULTATION_ENDPOINT` is reachable if consultation is enabled.
- [ ] Verify that `INVESTORCLAW_CONSULTATION_MODEL` is available on the endpoint if consultation is enabled.
- [ ] Set `INVESTORCLAW_CONSULTATION_HMAC_KEY`. The app generates it on first run.

- [ ] Prepare report directories.
- [ ] Make sure `INVESTOR_CLAW_REPORTS_DIR` is writable.
- [ ] Make sure `INVESTOR_CLAW_REPORTS_DIR` has enough disk space. 10 GB is recommended for 1000+ runs.
- [ ] Make sure `INVESTOR_CLAW_PORTFOLIO_DIR` contains portfolio CSV or Excel files.
- [ ] Configure automated backups for the reports directory.

### Review security and compliance

- [ ] Confirm secret management.
- [ ] Make sure no secrets are committed to git by running `git log -p | grep -i "password\|key\|secret"`.
- [ ] Rotate API keys.
- [ ] Set expiry reminders 30 days before rotation.
- [ ] Enable MFA on all external API accounts.
- [ ] Use API tokens for service accounts.
- [ ] Do not use personal credentials for service accounts.

- [ ] Confirm data privacy controls.
- [ ] Encrypt portfolio data at rest if you handle sensitive holdings.
- [ ] Enforce HTTPS for all API calls.
- [ ] Make sure logs contain no personal data. InvestorClaw runs an automatic sweep at startup.
- [ ] Verify GDPR and data residency compliance for cloud providers.

- [ ] Confirm network security.
- [ ] Open only the ports you need. Use `443` for HTTPS. Use `8080` only if you need a local GPU.
- [ ] Configure IP allowlists if you access the system from known networks.
- [ ] Use DNS names or hostnames in configuration.
- [ ] Do not hardcode IP addresses.
- [ ] Use a VPN or tunnel for sensitive environments, including air-gapped networks.

### Verify dependencies and compatibility

- [ ] Use a supported Python version.
- [ ] Install Python 3.10+.
- [ ] Prefer Python 3.10, 3.11, or 3.12.
- [ ] Do not use Python 3.9. macOS system Python often provides 3.9.
- [ ] Create a virtual environment with `python3.10 -m venv investorclaw-venv`.

- [ ] Install package dependencies.
- [ ] Install all packages with `pip install -r requirements.txt`.
- [ ] Check for version conflicts with `pip check`.
- [ ] Record pinned versions for reproducibility.
- [ ] Install optional cloud dependencies if needed.
- [ ] Install `together>=0.8.0` for Together.ai support.
- [ ] Install `anthropic>=0.9.0` for Claude consultation.

- [ ] Verify external services.
- [ ] Test all data provider endpoints with `curl`.
- [ ] Make sure Ollama or `llama-server` is running if consultation is enabled.
- [ ] Review cloud API quotas and monitoring.
- [ ] Configure fallback chains, such as Finnhub → Alpha Vantage → yfinance.

### Test and validate the deployment

- [ ] Run smoke tests.
- [ ] Run `investorclaw setup`. It should complete without errors.
- [ ] Run `investorclaw holdings`. It should fetch and price holdings.
- [ ] Run `investorclaw performance`. It should calculate Sharpe, beta, and max drawdown.
- [ ] Run `investorclaw bonds`. It should parse bond data correctly.
- [ ] Run `investorclaw news`. It should fetch portfolio news.
- [ ] Run `investorclaw analysis`. It should complete synthesis.

- [ ] Validate data quality.
- [ ] Make sure the portfolio CSV includes `Ticker`, `Shares`, and optional `Cost Basis`.
- [ ] Price five sample holdings with `investorclaw lookup AAPL`.
- [ ] Verify bond holdings parse correctly, including coupon %, maturity, and YTM calculations.
- [ ] Check outputs for `NaN`, `inf`, or `error` with `grep -i "nan\|inf\|error" eod_report.json`.

- [ ] Get stakeholder sign-off.
- [ ] Ask end users to review output formats, including JSON, CSV, and SVG cards.
- [ ] Ask finance and compliance to approve data residency and retention policies.
- [ ] Ask IT to approve network and firewall rules and API quotas.
- [ ] Ask legal to review API ToS and data sharing agreements.

## Deployment steps

Deploy InvestorClaw in this order.

### Prepare the infrastructure

```bash
# Clone repository from GitHub (canonical remote)
git clone https://gitlab.com/argonautsystems/InvestorClaw.git
cd InvestorClaw

# Verify git remote
git remote -v
# github (or origin) should point to github.com/argonautsystems/InvestorClaw

# Install via uv (canonical — reads pyproject.toml, produces .venv)
uv sync
source .venv/bin/activate
investorclaw --version
```

### Set up configuration

```bash
# Copy example environment
cp .env.example .env

# Edit .env with production values
nano .env

# Essential env vars to set:
#   - All API keys (FINNHUB_KEY, NEWSAPI_KEY, FRED_API_KEY, etc.)
#   - INVESTORCLAW_NARRATIVE_PROVIDER and endpoint
#   - INVESTOR_CLAW_REPORTS_DIR (writable, backed up)
#   - INVESTOR_CLAW_PORTFOLIO_DIR (contains portfolio CSVs)

# Verify configuration
investorclaw setup
```

### Validate data providers

```bash
# Test each provider
investorclaw lookup AAPL   # Price lookup
investorclaw analyst                # Analyst consensus (requires FINNHUB_KEY)
investorclaw news                   # Portfolio news (requires NEWSAPI_KEY)
investorclaw bonds                  # Bond analysis (requires FRED_API_KEY)

# Verify fallback chain works (if primary provider down)
unset FINNHUB_KEY && investorclaw analyst  # Should degrade gracefully
```

### Set up the narrative pipeline

```bash
# Activate stonkmode
openclaw agent -m "/portfolio stonkmode on"

# Test narration with a known portfolio
investorclaw holdings

# Verify stonkmode_narration JSON block appears in output
# If missing: check INVESTORCLAW_NARRATIVE_* env vars and provider connectivity
```

### Configure monitoring and alerting

```bash
# Configure log rotation (prevents disk fill)
cat > /etc/logrotate.d/investorclaw << EOF
/var/log/investorclaw/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0640 nobody investorclaw
}
EOF

# Set up monitoring alerts
# Alert on: API latency >5s, missing data points, stonkmode narration failures
# Tools: Datadog, New Relic, CloudWatch (depending on deployment platform)
```

### Configure backup and disaster recovery

```bash
# Daily backup of reports
0 2 * * * tar -czf /backups/investorclaw-$(date +\%Y\%m\%d).tar.gz /var/investorclaw/reports

# Test restore procedure monthly
tar -xzf /backups/investorclaw-20260416.tar.gz --dry-run

# Document recovery time objective (RTO): e.g., 1 hour
# Document recovery point objective (RPO): e.g., 24 hours
```

## Post-deployment verification

Verify the deployment immediately after release, again in week 1, and again in month 1.

### First 24 hours

- [ ] Monitor error logs with `tail -f /var/log/investorclaw/error.log`.
- [ ] Verify that all scheduled jobs run successfully.
- [ ] Check API quota usage for unexpected spikes.
- [ ] Review the first 100 portfolio analyses for correctness.
- [ ] Confirm that backup jobs completed.

### Week 1

- [ ] Analyze user adoption metrics.
- [ ] Measure average execution time by portfolio size.
- [ ] Track actual API spend against budget.
- [ ] Run a security audit. Confirm there are no secrets in logs and that authentication works.
- [ ] Collect stakeholder feedback on usability.

### Month 1

- [ ] Review capacity planning needs, including larger instances or more quotas.
- [ ] Check for critical dependency security patches.
- [ ] Review cost optimization opportunities across data providers.
- [ ] Confirm that `README` and `MODELS.md` are still accurate.
- [ ] Run a disaster recovery drill and test backup restoration.

## Production runbook

Use this runbook to diagnose common production issues.

### Narration does not emit

The most common cause is missing `INVESTORCLAW_NARRATIVE_*` variables or an unreachable endpoint.

> [!NOTE]
> Check both configuration and provider connectivity.

```bash
# Verify env vars
env | grep INVESTORCLAW_NARRATIVE

# Test endpoint connectivity
curl -v http://<endpoint>/v1/models  # or /api/tags for Ollama

# Re-activate stonkmode state file
openclaw agent -m "/portfolio stonkmode on"
```

### Bond analysis crashes on unusual coupon schedules

The usual cause is an edge case such as zero coupon or non-standard frequency.

Fix: Bond analyzer now uses `max(1, round(...))` for periods. Rebuild or upgrade to v1.0.1+.

### News fetch hangs or times out

The usual cause is a slow NewsAPI response or a rate limit.

```bash
# Increase timeout
INVESTORCLAW_API_TIMEOUT=30  # default 10s

# Or skip news for faster runs
INVESTORCLAW_SKIP_NEWS=true
```

### API costs are unexpectedly high

The usual cause is higher token usage or large context fetches.

```bash
# Reduce context window
INVESTORCLAW_NARRATIVE_MAX_TOKENS=500  # default 1024

# Or switch to budget model
INVESTORCLAW_NARRATIVE_MODEL=groq/openai/gpt-oss-120b
```

## Scaling and performance

Use this sizing guidance as a starting point.

| Deployment size | Scope | Compute | API quota | Cloud cost | Execution profile | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| Single Portfolio | `< 50 holdings` | 2 CPU, 4 GB RAM | ~100 requests/month | `<$1/month` | ~5–10 seconds per analysis | |
| Team/Firm | `50–500 holdings, 1–10 users` | 4 CPU, 8 GB RAM, SSD storage | ~1000 requests/month | `$10–50/month` | ~30–60 seconds for synthesis (parallelized) | |
| Enterprise | `500+ holdings, 50+ users, real-time` | 8+ CPU, 16+ GB RAM, NFS for reports | ~10,000+ requests/month | $100+/month (consider dedicated quota) | Cache price data. Pre-compute daily snapshots. | Consider load balancing, an API gateway, and a database such as PostgreSQL for portfolio history. |

## Decommissioning

When you retire InvestorClaw, complete these steps:

- [ ] Archive all reports to cold storage, such as AWS Glacier.
- [ ] Export final portfolio snapshots in CSV format for auditing.
- [ ] Rotate or revoke all API keys.
- [ ] Delete secrets from the credentials manager.
- [ ] Notify users of the sunset date with 30 days notice.
- [ ] Document all data retention requirements, including SEC and compliance requirements.

## References

- Configuration: See [CONFIGURATION.md](CONFIGURATION.md) for the full environment variable reference.
- Models: See [docs/MODELS.md](docs/MODELS.md) for tested model combinations.
- Architecture: See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).
- Support: GitHub Issues: https://gitlab.com/argonautsystems/InvestorClaw/-/issues

## Questions

Open an issue or contact `jperlow@gmail.com`.