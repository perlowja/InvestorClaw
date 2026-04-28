# InvestorClaw Security & Data Flow

**Version:** 2.1.9 | **Updated:** April 23, 2026 | **License:** Apache 2.0 Dual

---

## Executive Summary

InvestorClaw is a **local-first** portfolio analysis tool. By default, **all data stays on your machine**. External transmission is:
- **Disabled by default** (Ollama local mode for OpenClaw; Anthropic Claude for Claude Code)
- **Opt-in only** (requires explicit configuration)
- **Transparent** (documented in .env.example with examples)
- **Non-identifying** (summarized data, no account numbers/PII)

---

## Platform Configurations: Claude Code vs OpenClaw

### Claude Code (Default & Recommended)

**Narrative/Consultation Provider**: Claude Anthropic models (Haiku, Sonnet)
- No external configuration needed
- Data stays within Claude Code context (user's session)
- Optional: Configure local inference host for consultative LLM
- Default: Uses Anthropic models via Claude Code infrastructure

**Stonkmode**: Uses Anthropic models by default
- No external API calls unless explicitly configured
- If configured externally: Limited to trusted providers (Together, Groq, OpenAI, Google)

### OpenClaw (Advanced / Self-Hosted)

**Configuration Variability**: Much higher — users can choose:
- Local inference (Ollama, llama-server)
- Cloud providers (Together.ai, Groq, OpenAI, Google Gemini)
- Enterprise/custom endpoints
- Mix-and-match providers for different tasks

**Security Implications**: Users must vet their chosen providers
- Trusted providers: Together.ai, Groq, OpenAI, Google Gemini
- Not recommended: Unverified/untested endpoints
- All external transmission requires explicit user configuration

---

## Which Configuration Applies to You?

**Use Claude Code if:**
- Installing via Claude Code marketplace
- Want zero external configuration (Anthropic models by default)
- Prefer managed infrastructure (no local GPU needed)
- Want simple, safe defaults

**Use OpenClaw if:**
- Self-hosting OpenClaw agent
- Want to run inference locally (Ollama, llama-server on your GPU)
- Need to integrate with specific AI providers (Together, Groq, etc.)
- Want full control over computational resources and data routing

**Default configuration either way**: All data stays local (Ollama for OpenClaw, Claude Code context for Claude Code). No data leaves your machine unless explicitly configured.

---

## Data Flow Architecture

### Claude Code (Default Path — Local or Claude Infrastructure)

```
Your Portfolio (CSV/PDF)
         ↓
Python Computation (on your machine)
    • Parse holdings
    • Calculate metrics
    • Analyze performance
         ↓
Local JSON Reports (~portfolio_reports/)
         ↓
Claude Code Context (Anthropic models via Claude Code)
    • Haiku for Q&A (default)
    • Sonnet for synthesis (optional)
    ✅ Data flows through Claude Code session only
    ✅ NOT persisted externally
         ↓
Results to your terminal / artifact viewer

⚠️  Default: No external API calls beyond yfinance. No credential transmission.
```

**Optional: Local Inference Host**
If configured, consultative LLM runs on your machine (Ollama, llama-server):
```
Claude Code → Local llama-server (port 8080) → Results back to Claude Code
```

### OpenClaw (Configurable Path — More Provider Variability)

```
Your Portfolio (CSV/PDF)
         ↓
Python Computation (on your machine)
    • Parse holdings
    • Calculate metrics
    • Analyze performance
         ↓
Local JSON Reports (~portfolio_reports/)
         ↓
Configurable Narrative Provider:
    ├─ Local: Ollama/llama-server (no external transmission)
    ├─ Cloud (Trusted): Together.ai, Groq, OpenAI, Google Gemini
    │   Receives: Summarized portfolio text (tickers, values, returns)
    │   ✅ NOT account numbers
    │   ✅ NOT specific holdings
    │   ✅ NOT transaction history
    │   ✅ NOT identity data
    └─ Custom: User-configured endpoint (requires user vetting)
         ↓
Response: Comic narration (text) → back to stdout

⚠️  Default OpenClaw: Ollama (local, no transmission)
⚠️  If cloud: Verify provider is trusted before configuring
```

---

## Three Security Concerns & Clarification

### 1. Stonkmode Sends Portfolio to Together.xyz (Concern: Data Leakage)

**The Concern:**
> "Stonkmode sends tickers, values, G/L %, sector weights to Together.xyz by default."

**The Reality:**
- **Default provider:** `INVESTORCLAW_NARRATIVE_PROVIDER=ollama` (local)
- **Default endpoint:** Empty (not configured)
- **Default API key:** Empty (not provided)
- **To enable Together.xyz:** User must explicitly set three environment variables:
  ```bash
  INVESTORCLAW_NARRATIVE_PROVIDER=openai_compat
  INVESTORCLAW_NARRATIVE_ENDPOINT=https://api.together.xyz/v1
  INVESTORCLAW_NARRATIVE_API_KEY=<user_provided_key>
  ```

**What Gets Sent (if enabled):**

From `rendering/stonkmode.py:_summarize_holdings()`:
```
Total portfolio: $250,000
Equity: $175,000 (12 positions)
Bonds: $50,000 (3 positions)
Cash: $25,000
Unrealized G/L: +8.3%

Top 10 holdings:
  NVDA: $45,000 (18%, G/L +15%)
  MSFT: $35,000 (14%, G/L +22%)
  ...
```

**What Does NOT Get Sent:**
- ❌ Account numbers
- ❌ Broker identities
- ❌ Transaction history
- ❌ Personal identity data
- ❌ Cost basis details (only summary G/L %)

**User Control:**
Users can disable stonkmode entirely:
```bash
INVESTORCLAW_STONKMODE_DISABLED=true
```

Or keep it local:
```bash
INVESTORCLAW_NARRATIVE_PROVIDER=ollama
INVESTORCLAW_NARRATIVE_ENDPOINT=http://localhost:8080
```

---

### 2. identity_updater.py Injects Agent Instructions (Concern: Supply Chain / Prompt Injection)

**The Concern:**
> "A third-party skill can inject instructions into OpenClaw agent identity."

**The Reality:**

`setup/identity_updater.py` writes to `~/.openclaw/workspace/IDENTITY.md`:

```markdown
## InvestorClaw Data Integrity Rules

When working with InvestorClaw output, ALWAYS treat the output files as
the authoritative source of truth. Do NOT use cached session-context values.

Rule: File Authority
- Before citing any portfolio value, READ ~/portfolio_reports/holdings.json
- Extract from `data.summary.total_portfolio_value`
- NEVER paraphrase from memory
```

**Purpose:** Prevent Claude hallucination when citing stale cached values.
**Example hallucination risk:**
- Session 1: User uploads portfolio worth $100K
- Session 2: User uploads different portfolio worth $500K
- Without guardrail: Claude cites old session context, says "Your portfolio is $100K"
- With guardrail: Claude reads fresh file, says correct value

**Is this a security issue?**
- ✅ No, this is a data-integrity feature, not malicious injection
- ✅ Instructions are benign (read files, validate data)
- ✅ Transparent in code review
- ⚠️  But valid principle: Third-party skills should not modify agent identity without user consent

**Recommendation:**
Add explicit user prompt during setup:
```
This skill will add data-integrity rules to your OpenClaw IDENTITY file.
These rules ensure portfolio values are read from files, not cached memory.
[Allow / Deny]
```

---

### 3. Auto-Updater Runs git pull + pip install (Concern: Supply Chain / Arbitrary Code Execution)

**The Concern:**
> "Auto-updater pulls from repo and executes arbitrary code after user confirms."

**The Reality:**

`setup/update_checker.py:install_update()`:

```python
# 1. User is prompted to approve update
if prompt_update(update_info):
    # 2. Stash local changes (safe)
    git stash
    
    # 3. Fetch and pull from origin/main
    git fetch origin
    git pull origin main
    
    # 4. Run: pip install -r requirements.txt
    pip install -r requirements.txt
```

**Risk Factors:**
- ✅ Explicit user consent required
- ✅ Timeout protection (30-120 sec)
- ✅ Error handling and reporting
- ⚠️  BUT: No signature verification (rely on git + HTTPS)
- ⚠️  BUT: No pre-flight check (what changed in this update?)

**Mitigations Already In Place:**
- Git remote is over HTTPS (encrypted)
- GitHub/GitLab require auth for push
- Code is public and auditable
- Project has version tags for release pinning

**Recommendation:**
Add pre-update changelog display:
```python
# Before user confirms, show:
- Files changed
- Dependencies added/removed
- Commit messages in this release
```

---

## Default Configuration (Safe)

```bash
# Default .env (from .env.example)

# ✅ Local LLM consultation
INVESTORCLAW_CONSULTATION_ENABLED=false
INVESTORCLAW_CONSULTATION_ENDPOINT=http://localhost:8080

# ✅ Local stonkmode narration
INVESTORCLAW_NARRATIVE_PROVIDER=ollama
INVESTORCLAW_NARRATIVE_ENDPOINT=
INVESTORCLAW_NARRATIVE_API_KEY=

# ✅ Portfolio files stay local
INVESTOR_CLAW_PORTFOLIO_DIR=~/portfolios/
INVESTOR_CLAW_REPORTS_DIR=~/portfolio_reports/
```

**Result:** Zero external transmission. All processing local.

---

## How to Verify Data Doesn't Leave Your Machine

### 1. Check .env (Stonkmode)
```bash
grep NARRATIVE ~/.investorclaw/.env
# Should show: PROVIDER=ollama (or empty)
# If ENDPOINT=https://api.together.xyz/v1, data goes to cloud
```

### 2. Monitor Network (tcpdump / Wireshark)
```bash
tcpdump -i any -w portfolio.pcap 'port 443'
# Run: /ic-holdings
# Review pcap — should see only yfinance (market data), no custom endpoints
```

### 3. Check Report Files
```bash
ls ~/portfolio_reports/
# Should contain: holdings.json, performance.json, bonds.json, etc.
# These are local outputs. If no output, something failed (check logs).
```

### 4. Review Logs
```bash
python3 -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from commands.holdings import run
run({})
"
# Will show all external API calls (yfinance, Finnhub, etc.)
```

---

## Threat Model

### What InvestorClaw Does NOT Do

- ❌ Phone home with analytics
- ❌ Transmit portfolio data by default
- ❌ Create accounts or require login
- ❌ Store data in cloud (opt-in only)
- ❌ Modify system-wide configurations

### Realistic Risks

| Risk | Likelihood | Mitigation |
|------|------------|-----------|
| Local machine compromise | Low | HTTPS for all APIs, sandboxed Python |
| Git repo compromise | Very Low | GitHub/GitLab 2FA, signed commits |
| Dependency attack (pip) | Low | Lock requirements.txt, review updates |
| API key exposure | Medium | Use strong passwords, rotate keys |
| Stonkmode data leakage | Medium (if enabled) | Disable stonkmode or use local |

### Higher-Risk Configuration (OpenClaw Only)

If you enable stonkmode with external cloud provider (OpenClaw users):
```bash
INVESTORCLAW_NARRATIVE_PROVIDER=openai_compat
INVESTORCLAW_NARRATIVE_ENDPOINT=https://api.together.xyz/v1  # or other endpoint
INVESTORCLAW_NARRATIVE_API_KEY=sk-xxx
```

**Then:** Portfolio summary goes to configured cloud provider.

**Trusted Providers** (evaluated and recommended):
- ✅ Together.ai (Gemma, MiniMax, DeepSeek)
- ✅ Groq (fast inference)
- ✅ OpenAI (GPT models)
- ✅ Google Gemini (through official API)

**Not Recommended**:
- ❌ Unverified/untested endpoints
- ❌ Self-hosted services without security review
- ❌ Endpoints controlled by third parties you don't trust

**Mitigation:** Use local Ollama/llama-server instead (no external transmission)
**Risk Assessment:**
- If using trusted provider: Low risk (legitimate AI services, subject to their privacy policies)
- If using unverified provider: Medium-High risk (unknown handling of data)

---

## Recommendations for Implementation

### Claude Code

1. **Add user consent for identity_updater.py** (OpenClaw specific)
   - Display the rules being added
   - Let user approve before writing IDENTITY.md
   - Add `INVESTORCLAW_SKIP_IDENTITY_UPDATE=true` to opt out

2. **Document stonkmode data explicitly in code**
   - Add "Data Sent to Cloud" section in stonkmode.py docstring
   - Show exact format of summarized text
   - Link to this SECURITY.md

3. **Validate external narrative endpoints**
   - Claude Code: Use Anthropic models (no validation needed, integrated)
   - If user configures external endpoint: Validate it's on trusted list

### Both Platforms

4. **Add pre-update changelog** before git pull executes
   - Show: Files changed, dependencies added, commit messages
   - Let user review before proceeding

5. **Add flag to disable cloud narration entirely**
   - `INVESTORCLAW_NARRATIVE_DISABLED=true` (overrides all config)
   - Useful for restricted environments (CI, regulated industries)

6. **Sign releases with GPG**
   - Tag releases: `git tag -s v1.1.0`
   - Users verify: `git verify-tag v1.1.0`
   - Prevents man-in-the-middle attacks on git pull

### OpenClaw Specific

7. **Add provider vetting guidance**
   - Document which providers are trusted (Together, Groq, OpenAI, Google)
   - Warn against unverified/self-hosted endpoints
   - Allow users to opt into custom endpoints at their own risk

---

## References

- **Data Computation:** `commands/` (Python, all local)
- **Stonkmode Narration:** `rendering/stonkmode.py` (summarizers at line 668+)
- **Auto-Updater:** `setup/update_checker.py` (install_update function)
- **Identity Rules:** `setup/identity_updater.py`
- **Default Config:** `.env.example` (shows all defaults)

---

## Questions?

If you discover a security vulnerability:
- **Do NOT open a public issue**
- Email: jperlow@gmail.com with details
- Allow 48 hours for response before public disclosure

---

**Jason Perlow | Apache 2.0 Dual License | April 2026**
