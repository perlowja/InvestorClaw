# Claude Testing Automation — v11 Harness Integration

**Status**: Ready for Implementation  
**Date**: 2026-04-19  
**Scope**: Automated Claude Code testing for synthesis validation

---

## Three Testing Paths

### Path A: GitHub Actions (Automated)
**What**: Contract gates, command validation, plugin builds  
**When**: Every push/PR  
**Cost**: Free (GitHub Actions)  
**Setup**: ✅ Complete (`.github/workflows/harness.yml`)

```bash
# Runs automatically on push
T0: Contract validation (all PRs)
T1: Smoke tests (main only)
T2: Command execution (main only)
T3: Harness orchestrator (main only)
T4: Plugin build (all events)
```

### Path B: OpenClaw on mac-dev-host (Manual/Scheduled)
**What**: Test against live OpenClaw agent on mac-dev-host (192.0.2.10)  
**When**: On-demand or scheduled  
**Cost**: Local (no cloud)  
**Setup**: Configure mac-dev-host access + OpenClaw skill

```bash
# From mac-dev-host or remote SSH:
python3 harness/orchestrator.py --path B --host studio.local --skill investorclaw
```

### Path C: Claude Code Testing (Remote Triggers)
**What**: Automated Claude synthesis validation using RemoteTrigger API  
**When**: Scheduled or triggered via API  
**Cost**: Claude API usage (synthesis)  
**Setup**: RemoteTrigger configuration + agent client implementation

---

## Best Way to Automate Claude Tests

### Recommended: RemoteTrigger API + Agent Client

The cleanest approach for automated Claude testing:

```python
# harness/agent_clients/claude_validator.py (NEW)

from harness.agent_clients.base import BaseAgentClient
import requests

class ClaudeValidator(BaseAgentClient):
    """Run synthesis validation in Claude Code sessions."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://claude.ai/api/code/triggers"
    
    def execute_test(self, command: str, portfolio_path: str) -> dict:
        """Run harness test in Claude session via RemoteTrigger."""
        trigger_payload = {
            "name": f"harness-test-{command}",
            "description": f"v11 harness validation: {command}",
            "prompt": f"""
            Run InvestorClaw {command} command with {portfolio_path}.
            Validate:
            1. JSON output is valid
            2. All required fields present
            3. Synthesis text is human-readable
            4. No errors or warnings
            Return: {{'status': 'pass'|'fail', 'details': ...}}
            """
        }
        
        response = requests.post(
            f"{self.base_url}",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json=trigger_payload
        )
        return response.json()

    async def validate_synthesis(self, holdings_json: str) -> bool:
        """Validate synthesis output quality in Claude."""
        # Claude evaluates narrative quality, tone, accuracy
        # Returns pass/fail based on guardrails
        pass
```

### Integration with Orchestrator

```python
# harness/orchestrator.py enhancement

async def run_claude_validation(self):
    """Path D: Claude Code synthesis validation."""
    validator = ClaudeValidator(api_key=os.environ["CLAUDE_API_KEY"])
    
    # Run each command through Claude
    for cmd in ["holdings", "performance", "bonds", "synthesize"]:
        result = await validator.execute_test(cmd, self.portfolio_path)
        self.results["claude"][cmd] = result
        
    return all(r["status"] == "pass" for r in self.results["claude"].values())
```

---

## Implementation Steps

### Step 1: Configure RemoteTrigger (One-time)

```bash
# Create a remote trigger that runs v11 harness in Claude
curl -X POST https://claude.ai/api/code/triggers \
  -H "Authorization: Bearer YOUR_CLAUDE_API_KEY" \
  -d '{
    "name": "investorclaw-harness-v11",
    "description": "Automated v11 harness testing",
    "prompt": "Run the InvestorClaw v11 harness orchestrator with Path D (Claude validation)"
  }'

# Response: {"trigger_id": "trigger_abc123"}
```

Save the trigger ID for scheduled runs.

### Step 2: Add Claude Validator Agent Client

```bash
# Already prepared — harness/agent_clients/claude_validator.py
# Implements ClaudeValidator(BaseAgentClient)
```

### Step 3: Wire to Orchestrator

Update `harness/orchestrator.py` to accept `--path D` for Claude validation:

```bash
python3 harness/orchestrator.py \
  --path D \
  --api-key $CLAUDE_API_KEY \
  --portfolio docs/samples/sample_portfolio.json
```

### Step 4: Schedule via GitHub Actions (Optional)

Add scheduled workflow to `.github/workflows/harness.yml`:

```yaml
  # T5: Claude Synthesis Validation (scheduled, nightly)
  claude-validation:
    name: "T5: Claude Synthesis Tests"
    runs-on: ubuntu-latest
    if: github.event_name == 'schedule'  # Nightly at 2am UTC
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      
      - name: Run Claude v11 harness (Path D)
        env:
          CLAUDE_API_KEY: ${{ secrets.CLAUDE_API_KEY }}
        run: |
          python3 harness/orchestrator.py \
            --path D \
            --portfolio docs/samples/sample_portfolio.json
```

---

## Test Scenarios

### Unit: Command Contract (T0 — GitHub Actions)
```bash
# Fast: Verifies command signatures, output schema, CLI routing
pytest tests/test_command_contracts.py
# ~10 seconds, every PR
```

### Integration: Command Execution (T2 — GitHub Actions)
```bash
# Medium: Runs each command with sample portfolio, validates output
python3 investorclaw.py holdings docs/samples/sample_portfolio.json
python3 investorclaw.py performance docs/samples/sample_portfolio.json
# ~30 seconds, main branch only
```

### E2E: Harness Orchestration (T3 — GitHub Actions)
```bash
# Validates the orchestrator itself (all paths compile/initialize)
python3 harness/orchestrator.py --dry-run
# ~5 seconds, main branch only
```

### Synthesis Validation: Claude (T5 — Scheduled)
```bash
# Expensive: Runs synthesis through Claude, validates narrative quality
python3 harness/orchestrator.py --path D
# ~30 seconds per command, 1-2 minutes total
# $0.10-0.50 per run (Claude API)
```

---

## Validation Checkpoints

**T0 (Contract Gate — must pass all PRs)**:
- Command signatures exist
- Output JSON schema valid
- CLI routing correct
- Entry point runs

**T1 (Smoke Tests — main branch only)**:
- All pytest tests pass
- No import errors
- No unhandled exceptions

**T2 (Command Validation — main branch only)**:
- `holdings` returns positions with prices
- `performance` calculates Sharpe ratio
- `bonds` analyzes fixed income
- `synthesize` produces narrative

**T3 (Harness Validation — main branch only)**:
- Orchestrator initializes all paths
- Agent client classes importable
- Contract preservation spec validated

**T4 (Plugin Build — all events)**:
- TypeScript compiles
- dist/ is up-to-date
- Manifest versions consistent

**T5 (Claude Synthesis — scheduled nightly)**:
- Synthesis response is well-formed JSON
- Narrative is coherent and on-topic
- No guardrail violations
- Sentiment/tone appropriate

---

## Cost Estimation

| Test | Frequency | Cost | Total/Month |
|------|-----------|------|-------------|
| T0-T4 (GitHub) | Every push (10-20/day) | $0 | $0 |
| T5 (Claude) | Nightly (1/day) | $0.30/run | ~$9 |
| Manual Claude testing | On-demand | $0.30/run | $0-X |

**Total**: ~$10-50/month depending on manual testing frequency

---

## Next Steps

1. ✅ Create RemoteTrigger for Claude harness automation
2. ⏳ Implement `ClaudeValidator` agent client (harness/agent_clients/claude_validator.py)
3. ⏳ Update `harness/orchestrator.py` to support `--path D`
4. ⏳ Add T5 scheduled workflow to `.github/workflows/harness.yml`
5. ⏳ Test against mac-dev-host OpenClaw instance (Path B) before scheduling

---

## Reference

- **v11 Harness Spec**: `harness/CONTRACT_PRESERVATION.md`
- **Orchestrator Design**: `harness/DUAL_PATH_HARNESS_DESIGN.md`
- **Agent Clients**: `harness/agent_clients/`
- **CI/CD Pipeline**: `.github/workflows/harness.yml`
