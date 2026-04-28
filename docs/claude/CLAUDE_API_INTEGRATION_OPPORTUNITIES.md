# Claude API Integration Opportunities

**Status**: Audit Complete  
**Date**: 2026-04-19  
**Pattern**: Claude-native features with graceful open-source fallbacks for OpenClaw/Hermes Agent/ZeroClaw

---

## Overview

This document identifies where Claude's native APIs can be leveraged in Claude Code deployments while maintaining fallback compatibility for other platforms (OpenClaw, Hermes Agent, ZeroClaw).

**Key Pattern**: Detect `INVESTORCLAW_DEPLOYMENT_MODE=claude_code` and use Claude API where available, with automatic fallback to open-source libraries.

---

## High-Impact Integration Opportunities

### 1. **Vision API for PDF/Image Analysis** ✅ IMPLEMENTED

**Location**: `/services/pdf_extraction_dual_mode.py`

**Current Status**: Dual-mode PDF extraction operational
- **Claude Code**: Sends PDF pages as images to Claude with portfolio extraction prompt
- **Other Platforms**: Falls back to regex-based extraction

**Accuracy Benefits**:
- Handles scanned PDFs (regex fails on these)
- Detects broker platform automatically  
- Extracts complex multi-page statements
- Handles non-standard formats

**Code Pattern**:
```python
def detect_extraction_mode() -> ExtractionMode:
    if os.getenv("INVESTORCLAW_DEPLOYMENT_MODE") == "claude_code":
        return ExtractionMode.CLAUDE_VISION  # Claude API
    return ExtractionMode.REGEX  # Fallback
```

**Recommended Extensions**:
- Chart screenshot analysis (dashboard OCR)
- Statement header/footer analysis
- Handwritten notes extraction

---

### 2. **File API for Session State (Batch Processing)**

**Potential Location**: `/commands/analyze_performance_polars.py`

**Use Case**: Large portfolio analysis (100+ positions)

**Current**: Re-computes metrics on each call
**Claude Enhancement**: Use Files API to cache:
- Daily price history (50KB per 100 positions)
- Calculated returns and volatility
- Benchmark correlation matrices

**Benefits**:
- 90% faster re-analysis of same portfolio
- Persistent session state across API calls
- Reduced token usage (reuse file across requests)

**Implementation Pattern**:
```python
def get_cached_analysis(portfolio_id: str):
    if os.getenv("INVESTORCLAW_DEPLOYMENT_MODE") == "claude_code":
        # Try Claude Files API cache
        file_id = fetch_cached_file(portfolio_id)
        if file_id:
            return use_cached_file(file_id)  # 90% faster
    # Fall back to recompute
    return compute_analysis()
```

**Complexity**: Medium (1-2 weeks integration)

---

### 3. **Vision API for Chart Analysis & Validation**

**Location**: `/rendering/artifact_generator.py` and `/commands/dashboard.py`

**Use Case**: Validate dashboard charts for data accuracy

**Current**: Plotly generates charts client-side; no server-side validation
**Claude Enhancement**: Analyze rendered charts with vision to:
- Detect anomalies (sudden spikes, missing data)
- Verify axis scaling correctness
- Validate legend and annotations
- Cross-check against source data

**Benefits**:
- Catch data errors before display
- Automated chart quality assurance
- User-friendly anomaly alerts

**Implementation Pattern**:
```python
def validate_chart(chart_html: str, source_data: dict) -> ChartValidation:
    if os.getenv("INVESTORCLAW_DEPLOYMENT_MODE") == "claude_code":
        # Render chart to image, analyze with vision
        img = render_chart_image(chart_html)
        return claude.vision_analyze(img, "Validate this chart against source data")
    # Fallback: basic numeric range checks
    return basic_validation(source_data)
```

**Complexity**: Medium (1 week integration)

---

### 4. **Structured Output (Tool Use) for Analysis Results**

**Location**: `/commands/synthesize_analysis.py`

**Use Case**: Multi-step portfolio analysis with guaranteed JSON output

**Current**: Manual JSON serialization, error-prone
**Claude Enhancement**: Use native JSON mode or structured output to:
- Guarantee valid JSON results
- Type-safe portfolio recommendations
- Structured risk alerts
- Compliance-ready audit trails

**Benefits**:
- Zero JSON parsing errors
- Native type validation
- Better interoperability

**Implementation Pattern**:
```python
def synthesize_portfolio(holdings: dict):
    if os.getenv("INVESTORCLAW_DEPLOYMENT_MODE") == "claude_code":
        # Use Claude's native structured output
        return claude.messages.create(
            ...,
            response_format=PortfolioAnalysisSchema  # Pydantic model
        )
    # Fallback: parse LLM text output
    return parse_structured_text()
```

**Complexity**: Low (1-2 days, mostly schema definition)

---

### 5. **200K Token Context for Large Portfolio Analysis**

**Location**: `/commands/analyze_performance_polars.py`

**Use Case**: Analyze mega-portfolios (500+ positions) with multi-year history

**Current**: Limited to recent positions/returns due to context limits
**Claude Enhancement**: Use extended context to:
- Analyze full 10-year portfolio history in single call
- Include all historical transactions
- Generate comprehensive attribution analysis
- Multi-factor decomposition

**Benefits**:
- Comprehensive historical analysis in one call
- Better pattern detection (cycles, rebalancing events)
- Holistic portfolio view

**Implementation Pattern**:
```python
def comprehensive_analysis(holdings: dict, years: int = 10):
    if os.getenv("INVESTORCLAW_DEPLOYMENT_MODE") == "claude_code":
        # Can include full history in context
        context_size = estimate_tokens(holdings, years)
        if context_size < 200_000:
            return claude_deep_analysis(holdings, years=years)
    # Fallback: analyze recent data only
    return incremental_analysis(holdings, years=min(years, 3))
```

**Complexity**: Medium (1-2 weeks, mainly data prep)

---

### 6. **Batch API for Overnight Analysis Jobs**

**Location**: `/commands/pipeline.py` (full analysis pipeline)

**Use Case**: Scheduled EOD analysis, overnight portfolio optimization

**Current**: Runs synchronously; blocks on API calls
**Claude Enhancement**: Use Batch API for:
- Overnight scenario analysis (100 scenarios in parallel)
- Tax-loss harvesting optimization (GPU equivalent)
- Peer comparison (compare against 1000 portfolios)
- Daily/weekly report generation

**Benefits**:
- 50% cheaper API costs (Batch API pricing)
- Results ready by morning (no waiting)
- Parallel scenario testing

**Implementation Pattern**:
```python
def schedule_overnight_analysis(portfolio: dict):
    if os.getenv("INVESTORCLAW_DEPLOYMENT_MODE") == "claude_code":
        # Submit batch of 100 scenario jobs
        batch_id = claude.batches.create(requests=[...])
        schedule_retrieval(batch_id, check_time="6:00 AM")  # Check next morning
        return "Analysis scheduled; results ready by 6 AM"
    # Fallback: synchronous analysis
    return synchronous_analysis(portfolio)
```

**Complexity**: Medium (1-2 weeks, batch infrastructure setup)

---

## Lower-Impact Opportunities

### 7. **Image Generation for Portfolio Reports**

**Location**: `/rendering/eod_email_template.py`

**Use Case**: Include custom portfolio summary charts in emails

**Current**: Static HTML charts (Plotly)
**Claude Enhancement**: Generate custom infographics with:
- Allocation breakdown visualization
- Risk heatmap
- Performance timeline
- Custom color schemes

**Benefits**: More professional reports, branded for enterprise use

**Complexity**: Low-medium (1 week)

---

### 8. **Natural Language Query Support**

**Location**: `/runtime/router.py` (command routing)

**Use Case**: "What are my top 3 risks?" instead of `/ic-analyze-risk`

**Current**: Fixed command syntax only
**Claude Enhancement**: Use Claude to:
- Parse natural language portfolio queries
- Route to appropriate analysis command
- Format results in response style

**Benefits**: Better UX for non-technical users

**Complexity**: Low (3-5 days, mostly prompt engineering)

---

## Implementation Priority

### **Phase 1** (Weeks 1-2): High-impact, Low Complexity
1. ✅ Dual-mode PDF extraction (DONE)
2. Structured output for analysis (easy schema work)
3. Natural language query support (prompt engineering)

### **Phase 2** (Weeks 3-4): Medium Complexity, High Value
1. Chart analysis & validation (vision + fallback)
2. Session state caching (Files API)
3. Extended context analysis (200K tokens)

### **Phase 3** (Weeks 5-6): Infrastructure Setup
1. Batch API for overnight jobs
2. Image generation for reports

---

## Fallback Pattern Template

All integrations follow this pattern:

```python
import os

def feature_with_claude_fallback(data):
    deployment_mode = os.getenv("INVESTORCLAW_DEPLOYMENT_MODE", "").lower()
    
    # Try Claude API if in Claude Code mode
    if deployment_mode == "claude_code":
        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            result = client.messages.create(...)
            return result
        except (ImportError, Exception) as e:
            logger.warning(f"Claude API not available: {e}. Using fallback.")
    
    # Fallback: use open-source libraries
    return fallback_implementation(data)
```

---

## Configuration

**Environment Variables**:
```bash
# Deployment mode detection
INVESTORCLAW_DEPLOYMENT_MODE=claude_code  # or openai, standalone, etc.

# Claude API authentication (only needed if using vision/files/batch)
ANTHROPIC_API_KEY=sk-ant-...

# Feature flags (optional; can be inferred from mode)
INVESTORCLAW_USE_CLAUDE_VISION=true
INVESTORCLAW_USE_CLAUDE_FILES=true
INVESTORCLAW_USE_CLAUDE_BATCH=false
```

---

## Security & Cost Considerations

### Security
- Never expose API keys in public repos (already in .gitignore)
- Vision API processes user PDFs; ensure they understand data handling
- Files API stores portfolio data; use expiration policies

### Cost
- Vision API: ~$0.003 per page (vs $0 for regex)
- Files API: $0.20 per GB/day (minimal for portfolio data)
- Batch API: 50% discount (good for overnight jobs)
- Structured output: No extra cost (part of token usage)

**Total Estimated Monthly Cost** (100-user tier):
- Vision PDF extraction: ~$10/month (50 uploads × 5 pages × $0.003)
- Files API caching: ~$1/month (10 GB × $0.20/day)
- Batch API: Depends on usage (break-even at 20+ overnight runs/day)

---

## References

- [Claude API Documentation](https://docs.anthropic.com/claude)
- [Vision API Guide](https://docs.anthropic.com/vision)
- [Files API Guide](https://docs.anthropic.com/files)
- [Batch API Guide](https://docs.anthropic.com/batches)
- [Current Implementation](./pdf_extraction_dual_mode.py)

---

**Next Steps**: Start with Phase 1 integrations (weeks 1-2) for high-impact, low-risk wins.
