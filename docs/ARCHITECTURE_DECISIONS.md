# InvestorClaw Architectural Decisions

**Audience**: Tech leads and architects  
**Status**: Production-Grade Architecture  
**Last Updated**: April 2026  
**See also**: [ARCHITECTURE_INDEX.md](ARCHITECTURE_INDEX.md) for architecture guide | [ARCHITECTURE.md](ARCHITECTURE.md) for code structure

**Reference**: [Beyond the Demo: What It Actually Takes to Build a Production-Grade Agentic Skill](https://techbroiler.net/beyond-the-demo-what-it-actually-takes-to-build-a-production-grade-agentic-skill/)

---

## Executive Summary

InvestorClaw is built on the principle that **the LLM synthesizes language; Python handles everything else**. This architectural decision cascades through every design choice, creating a resilient, auditable, and deterministic financial analysis system suitable for real investor use.

---

## Core Architectural Principles

### 1. Separation of Concerns: LLM Synthesis vs. Computation

**Decision**: The language model's sole responsibility is synthesis—converting pre-computed financial data and analysis into natural language responses. All deterministic computation occurs in Python before the model ever processes the data.

**Rationale**:
- LLMs are unreliable for arithmetic; Python is deterministic
- Separating concerns enables independent testing and auditability
- Model output can be validated against Python-computed ground truth
- Enables safe deployment to regulated environments (individual investors, registered advisors)

**Implementation**:
```python
# Python layer: deterministic computation
portfolio_metrics = {
    "yield_to_maturity": calculate_ytm(bond_data),
    "duration": calculate_duration(bond_data),
    "performance": calculate_performance(holdings),
    "risk_metrics": compute_risk_analytics(portfolio)
}

# LLM layer: synthesis only (no math)
response = synthesize_analysis(portfolio_metrics, user_context)
```

**Evidence**: All financial metrics in holdings, bonds, performance, and analyst commands are computed in `services/` modules (consultation_policy, portfolio_utils) before reaching the language model.

---

### 2. Deterministic Computation for Financial Calculations

**Decision**: Every financial metric—yield-to-maturity, duration, performance analytics, risk measures—must be computed deterministically in Python, never inferred from language model output.

**Rationale**:
- Financial accuracy is non-negotiable; LLMs cannot guarantee precision
- Enables audit trails and regulatory compliance
- Supports repeatable, testable analysis workflows
- Preserves investor trust through transparency

**Implementation**:
- `services/portfolio_utils.py`: Core financial computation engine
- `models/holdings.py`: Portfolio data structures with computed properties
- `internal/tier3_enrichment.py`: Tier-3 enrichment with deterministic attribution

**Testing**: Unit tests validate all financial calculations against reference implementations.

---

### 3. Provider Resilience Through Graceful Degradation

**Decision**: Implement a four-tier fallback chain for market data. If the primary provider fails, the system degrades gracefully rather than collapsing.

**Rationale**:
- Single points of failure are unacceptable in production systems
- Network failures, rate limits, and provider downtime are inevitable
- Graceful degradation maintains user experience under adverse conditions
- "An agentic skill that collapses when one provider is unavailable isn't a skill. It's a fragile demo."

**Implementation**:
```python
# Fallback chain (in providers/)
1. Primary provider (Polygon, Finnhub, or NewsAPI)
2. Secondary provider (Alpha Vantage, IEX Cloud)
3. Cached data from recent runs
4. Synthetic or last-known-good data
```

**Evidence**:
- `providers/price_provider.py`: Multi-provider market data with fallbacks
- `providers/fetch_bond_data.py`: Bond data sourcing with degradation
- `services/portfolio_utils.py`: Persistent cache for degraded-mode operation

---

### 4. Context Window Management and Compression

**Decision**: Treat context as a scarce resource. Compress portfolio data aggressively—reducing ~72,000 tokens to <1,000 tokens for LLM input—while preserving full artifacts separately for audit and review.

**Rationale**:
- Context window is the primary cost and latency lever
- Compression preserves model performance while reducing API costs
- Full artifacts enable human review without model inference
- Enables longer, more sophisticated reasoning within model constraints

**Implementation**:
```python
# Compression strategy:
# - Holdings: Compact JSON (ticker, shares, cost, current value)
# - Bonds: Reduced duration/yield metrics only
# - Performance: Aggregated returns by period
# - Risk: Summary statistics (volatility, correlation, VaR)

# Output contracts:
# - Compact stdout: <1,000 tokens for agent consumption
# - Full disk artifacts: CSV, JSON, HTML for human review
```

**Evidence**:
- `rendering/compact_serializers.py`: Aggressive token-aware compression
- `services/context_window_monitor.py`: Token accounting and enforcement
- `rendering/disclaimer_wrapper.py`: Output validation and disclaimer injection
- All commands implement dual-output pattern (stdout + disk artifact)

---

### 5. Structured Guardrails as Rules Engine

**Decision**: Enforce output policies through a rules engine that validates actual model output, rather than relying solely on prompt instructions.

**Rationale**:
- Prompt instructions are best-effort; rules are enforceable
- Different deployment contexts require different policies:
  - Individual investor: Educational disclosures, no direct recommendations
  - Registered advisor: Full fiduciary compliance, regulatory attestation
  - Institutional: Risk limits, portfolio constraints, position tracking
- Output validation is cheaper than regenerating non-compliant responses

**Implementation**:
```python
# Guardrails enforcer (config/guardrail_enforcer.py)
class GuardrailEnforcer:
    def __init__(self, mode: DeploymentMode):
        # Mode: SINGLE_INVESTOR → EDUCATIONAL guardrails
        #       FA_PROFESSIONAL → ADVISORY guardrails
        self.mode = mode
        
    def check_recommendation(self, text: str) -> Tuple[bool, str]:
        # EDUCATIONAL: No directives (sell/buy), requires conditional language
        # ADVISORY: No language restrictions (advisor responsibility)
        
    def enforce_recommendation(self, text: str) -> str:
        # Automatically rewrite non-compliant text
        # Replace directives with conditional language
        # Add disclaimers and audit trails
```

**Evidence**:
- `data/guardrails.yaml`: Policy definitions by deployment mode
- `config/guardrail_enforcer.py`: Output validation and automatic remediation
- `config/deployment_modes.py`: SINGLE_INVESTOR vs FA_PROFESSIONAL mode switching
- `investorclaw.py`: Pre-flight guardrail priming via `_auto_prime_guardrails()`

---

### 6. Comprehensive Testing Framework

**Decision**: Treat test infrastructure as production code. Implement:
- 442+ unit tests (core logic, calculation accuracy, serialization)
- 114 workflow validations (14 quality dimensions)
- 18 smoke tests (end-to-end command execution)

**Rationale**:
- Financial software demands high test coverage
- Tests serve as executable documentation
- Continuous validation prevents regression
- Enables safe refactoring and optimization

**Test Categories**:
1. **Calculation Tests**: Financial metric accuracy against reference data
2. **Contract Tests**: Command output shape and required fields
3. **Integration Tests**: Multi-step workflows with real data
4. **Regression Tests**: Known issues and edge cases
5. **Compliance Tests**: Guardrail enforcement and disclosure validation

**Evidence**: `tests/` directory with pytest configuration and smoke test suite

---

### 7. Data Governance and Security

**Decision**: Implement layered data protection:
- PII scrubbing before external API calls
- Injection-pattern detection (prompt injection, SQL injection)
- Fingerprint chains for attribution verification
- Encryption for sensitive artifacts

**Rationale**:
- User portfolios contain personal financial data (PII/PHI)
- External API calls may be logged or monitored
- Injection attacks can corrupt model reasoning or leak data
- Audit trails must be tamper-evident

**Implementation**:
```python
# Data flow:
# 1. Load portfolio → Validation and normalization
# 2. Enrich with market data → Tier-3 enrichment with constraints
# 3. Compute metrics → HMAC fingerprinting for audit trail
# 4. Prepare LLM input → Context compression (<1000 tokens)
# 5. Store artifacts → Disk-based with read restrictions and status tracking
```

**Fingerprinting in consultation_policy.py**:
```python
def update_session_fingerprint(prev_fp: str, symbol: str, synthesis: str) -> str:
    """Chain HMAC: HMAC-SHA256(key, prev_fp + symbol + synthesis)[:16]"""
    key = os.environ.get("INVESTORCLAW_CONSULTATION_HMAC_KEY", "")
    msg = f"{prev_fp}{symbol}{synthesis}".encode()
    return _hmac.new(key, msg, hashlib.sha256).hexdigest()[:16]
```

**Evidence**:
- `internal/tier3_enrichment.py`: Core enrichment with PII handling
- `services/consultation_policy.py`: HMAC fingerprinting for attribution (`update_session_fingerprint`)
- `services/extract_pdf.py`: PDF extraction with data validation
- `config/guardrail_enforcer.py`: Output validation and remediation across deployment modes

---

## Architectural Patterns

### Dual-Output Pattern

Every analysis command produces two outputs:

1. **Compact stdout** (~500-1000 tokens)
   - Intended for OpenClaw agent consumption
   - Optimized for token efficiency
   - Serialized as JSON for structured parsing

2. **Full disk artifact** (CSV/JSON/HTML)
   - Intended for human review
   - Preserves complete analysis for audit
   - Enables downstream tooling (pivot tables, charting)

### Multi-Tier Consultation

Commands support three consultation tiers:

1. **Tier 1**: Local computation only (no external enrichment)
2. **Tier 2**: Basic enrichment (market data, news headlines)
3. **Tier 3**: Deep enrichment (analyst metrics, sentiment analysis, custom models)

### Command Dispatch Pattern

```
investorclaw.py (entry point)
  ├─ Bootstrap: Load env, config, auth
  ├─ Resolve: Find command script from registry
  ├─ Synthesize: Build defaults from recent artifacts
  ├─ Prime: Apply guardrails if needed
  └─ Dispatch: Run command with environment context
  
Command module (e.g., commands/fetch_holdings.py)
  ├─ Load: Fetch portfolio and market data
  ├─ Compute: Calculate metrics and analytics
  ├─ Render: Compact stdout + full artifact
  └─ Return: JSON to OpenClaw agent
```

---

## Deployment Modes

### Individual Investor Mode
- **Guardrails**: Educational only, no direct recommendations
- **Data**: Full portfolio transparency (no PII filtering)
- **Compliance**: Disclosures about performance, not guarantees
- **Access**: Single-user, local execution or personal OpenClaw gateway

### Registered Advisor Mode
- **Guardrails**: Fiduciary compliance, regulatory attestation
- **Data**: Comply with Regulation SHO, beneficial ownership reporting
- **Compliance**: Full audit trail, regulatory validation
- **Access**: Multi-user, enterprise gateway, encrypted storage

### Institutional Mode
- **Guardrails**: Risk limits, position tracking, hedging requirements
- **Data**: Real-time feeds, regulatory reporting interfaces
- **Compliance**: Continuous monitoring, automated alerts
- **Access**: Batch processing, API integrations, SLA enforcement

---

## Quality Assurance

### Quality Dimensions (14 total)

1. **Calculation Accuracy**: Financial metrics match reference implementations
2. **Completeness**: All required fields present in output
3. **Consistency**: Holdings reconcile across commands
4. **Currency**: Data freshness within acceptable bounds
5. **Attribution**: All calculations traceable to source data
6. **Compliance**: Guardrails enforced end-to-end
7. **Performance**: Response time within latency budget
8. **Availability**: Graceful degradation under provider failure
9. **Security**: PII protected, injections detected
10. **Clarity**: Language output is clear and actionable
11. **Explainability**: User understands metric definitions
12. **Reliability**: Repeatable results across runs
13. **Auditability**: Complete audit trail of decisions
14. **Accessibility**: Output consumable by agents and humans

---

## Future Architectural Considerations

### Scaling to Multi-Portfolio Management
- Parallel processing of multiple portfolios
- Cached aggregated benchmarks
- Rate-limiting strategies for external APIs

### Real-Time Alerting
- Event-driven market data ingestion
- Continuous guardrail validation
- Webhook notifications for portfolio changes

### Model Agility
- Support for multiple LLM backends (OpenAI, Anthropic, local)
- Model swap without architectural changes
- Context compression independent of model choice

### Regulatory Reporting
- Automated SEC/FINRA compliance exports
- Audit log serialization and signing
- Integrated with financial reporting systems

---

## Decision Rationale Summary

| Principle | Problem Solved | Trade-offs |
|-----------|----------------|-----------|
| LLM synthesis only | Arithmetic errors, unreliability | Extra Python layer complexity |
| Deterministic computation | Audit trail, consistency | No fancy LLM-based analytics |
| Provider resilience | Single-point failures | Cache staleness, degraded mode tradeoffs |
| Context compression | Token cost, latency | Development overhead for dual-output |
| Structured guardrails | Prompt-following unreliability | Rules-engine maintenance burden |
| Comprehensive testing | Regression, edge cases | QA infrastructure investment |
| Data governance | Security/compliance risk | Encryption/obfuscation overhead |

---

## References

- **Blog Post**: [Beyond the Demo: What It Actually Takes to Build a Production-Grade Agentic Skill](https://techbroiler.net/beyond-the-demo-what-it-actually-takes-to-build-a-production-grade-agentic-skill/)
- **Code Structure**: See `ARCHITECTURE.md` for module organization
- **Guardrails Policy**: `data/guardrails.yaml`
- **Testing**: `tests/` and `tests_smoke.py`
- **Provider Strategy**: `providers/` module

---

**Document Maintainers**: @perlowja  
**Last Review**: April 2026  
**Next Review**: July 2026
