# V11 Harness Quick Start — Multi-Device & LLM Provider Testing

**Status**: Phase 1 (Device Infrastructure) Complete  
**Date**: 2026-04-19  
**Scope**: Device matrix, command matrix, provider matrix, remediation workflows

---

## What's New in Restored V11

### Phase 1: Device Infrastructure ✅
- **device_matrix.py**: mac-dev-host (Mac), pi-large (8GB Pi), pi-small (2GB Pi)
- **Timeout scaling**: Device-specific latency multipliers
- **SSH support**: ZeroClaw integration for remote Pi testing

### Phase 2: LLM Provider Matrix (In Development)
- **provider_matrix.py**: xAI Grok, Google Gemini, Together AI, Gemma-4
- **Provider clients**: Per-provider implementations
- **Fallback logic**: Graceful degradation on provider failures

### Phase 3: Full Command Coverage (In Development)
- **command_matrix.py**: All 22 commands organized by tier
- **Tier 1** (fast): holdings, performance, bonds, analyst, news, etc. (10 commands)
- **Tier 2** (medium): eod-report, session, fa-topics, lookup, etc. (10 commands)
- **Tier 3** (slow): help, setup, run (2 commands)

### Phase 4: Remediation Workflows ✅
- **remediation.py**: CAP1-CAP6 automatic failure recovery
- CAP1: Orchestration failure recovery
- CAP2: Provider degradation fallback
- CAP3: Device unreachable handling
- CAP4: Memory pressure response
- CAP5: ZeroClaw routing failure
- CAP6: Model mismatch recovery

---

## Running the Harness

### 1. Basic Usage (Single Scenario)

```bash
# Run a single test scenario on mac-dev-host (default)
python3 harness/orchestrator.py

# Run a scenario on a specific device
python3 harness/orchestrator.py --device mac-dev-host     # Mac (local)
python3 harness/orchestrator.py --device pi-large     # 8GB Pi (remote SSH)
python3 harness/orchestrator.py --device pi-small     # 2GB Pi (constrained)
```

### 2. Command Tiers

```bash
# Run Tier 1 (fast, ~10 commands, ~1-2 minutes)
python3 harness/orchestrator.py --tier 1 --device mac-dev-host

# Run Tier 2 (medium, 10 more commands, ~3-5 minutes)
python3 harness/orchestrator.py --tier 2 --device mac-dev-host

# Run Tier 3 (slow, all commands, ~5-10 minutes)
python3 harness/orchestrator.py --tier 3 --device mac-dev-host
```

### 3. Device Matrix Testing

```bash
# Fast validation across all devices (Tier 1 only)
for device in mac-dev-host pi-large pi-small; do
  echo "Testing $device..."
  python3 harness/orchestrator.py --tier 1 --device $device
done

# Full command suite on single device
python3 harness/orchestrator.py --tier 3 --device mac-dev-host

# Full command suite on constrained Pi
python3 harness/orchestrator.py --tier 3 --device pi-small
```

### 4. Provider Testing (Coming Next)

```bash
# Run commands with specific providers (Phase 2)
python3 harness/orchestrator.py --provider xai      # xAI Grok
python3 harness/orchestrator.py --provider google   # Google Gemini
python3 harness/orchestrator.py --provider together # Together AI
python3 harness/orchestrator.py --provider gemma    # Local Gemma-4
```

---

## Test Matrix After Full Restoration

```
DEVICES (3):
  ✅ mac-dev-host (Mac, local, 16GB)
  ⏳ pi-large (Pi 8GB, remote SSH)
  ⏳ pi-small (Pi 2GB, constrained)

LLM PROVIDERS (4):
  ⏳ xAI (Grok-4.1)
  ⏳ Google (Gemini-2.5-Flash)
  ⏳ Together (MiniMax-M2.7)
  ⏳ Gemma (local Ollama)

COMMANDS (22):
  ⏳ All core analysis + reporting + setup

REMEDIATION (6 CAPs):
  ✅ CAP1: Orchestration recovery
  ✅ CAP2: Provider degradation
  ✅ CAP3: Device unreachable
  ✅ CAP4: Memory pressure
  ✅ CAP5: ZeroClaw routing
  ✅ CAP6: Model mismatch

TOTAL MATRIX: 3 devices × 4 providers × 22 commands = 264 test scenarios
```

---

## Environment Setup

### mac-dev-host (Mac, Local)
```bash
# No setup required (local execution)
python3 harness/orchestrator.py --device mac-dev-host
```

### pi-large (8GB Raspberry Pi)
```bash
# Set SSH config (one-time)
export ZEROCLAW_HOST=pi-large.local
export ZEROCLAW_USERNAME=user

# Run tests via SSH
python3 harness/orchestrator.py --device pi-large
```

### pi-small (2GB Raspberry Pi)
```bash
# Set SSH config (one-time)
export ZEROCLAW_HOST=pi-small.local
export ZEROCLAW_USERNAME=user

# Run tests via SSH (will trigger memory pressure tests)
python3 harness/orchestrator.py --device pi-small --tier 1
```

---

## File Structure

```
harness/
  ✅ orchestrator.py              # Main harness (updated with device support)
  ✅ device_matrix.py             # Device configurations
  ✅ command_matrix.py            # Command definitions
  ✅ provider_matrix.py           # LLM provider configurations
  ✅ remediation.py               # CAP1-CAP6 workflows
  ✅ CONTRACT_PRESERVATION.md    # Contract system documentation
  ✅ V11_RESTORATION_PLAN.md     # Full restoration roadmap
  ✅ QUICK_START.md              # This file
  
  agent_clients/
    ✅ base.py                    # AgentClient base class
    ✅ openclaw.py               # OpenClaw client
    ✅ zeroclaw.py               # ZeroClaw client (SSH support)
    
  recordings/
    📁 (Test results stored here)
```

---

## Expected Test Runtimes

### Single Command
- mac-dev-host: 1-5s
- pi-large: 1.5-8s (timeout multiplier 1.5x)
- pi-small: 2.5-12.5s (timeout multiplier 2.5x)

### Tier 1 (10 commands)
- mac-dev-host: ~20-50s
- pi-large: ~30-75s
- pi-small: ~60-150s

### Tier 2 (10 commands)
- mac-dev-host: ~30-60s
- pi-large: ~45-90s
- pi-small: ~90-200s

### Tier 3 (22 commands)
- mac-dev-host: ~60-120s (1-2 minutes)
- pi-large: ~90-180s (1.5-3 minutes)
- pi-small: ~180-400s (3-6 minutes)

---

## Troubleshooting

### Device Unreachable
```bash
# Check SSH connectivity
ssh user@pi-large.local "echo OK"

# Set custom host
export ZEROCLAW_HOST=192.0.2.56  # Use IP instead of hostname
```

### Commands Timing Out
- Increase timeout: Add `--timeout 30` (in seconds)
- Reduce concurrency: pi-small has `max_concurrent_commands: 1`

### Memory Pressure on pi-small
- Run Tier 1 only: `--tier 1 --device pi-small`
- CAP4 (memory pressure) automatically reduces concurrency

### Import Errors
```bash
# Make sure you're in the harness directory
cd InvestorClaw/harness/

# Or add to PYTHONPATH
export PYTHONPATH="$PWD:$PYTHONPATH"
python3 orchestrator.py
```

---

## Next Steps (Phase 2-3)

### Phase 2: LLM Provider Matrix (In Progress)
- [ ] Implement provider_client.py with xAI, Google, Together, Gemma support
- [ ] Add provider reachability checks (T0 phase)
- [ ] Add API key validation (T1 phase)
- [ ] Test all 4 providers with holdings command

### Phase 3: Full Command Coverage (In Progress)
- [ ] Test all Tier 1 commands (fast validation)
- [ ] Test all Tier 2 commands (medium validation)
- [ ] Test all Tier 3 commands (slow validation)
- [ ] Establish performance baselines

### Success Criteria
- ✅ All 264 scenarios executable (3 devices × 4 providers × 22 commands)
- ✅ Multi-device SSH+ZeroClaw working
- ✅ Provider matrix validated
- ✅ All 22 commands tested
- ✅ 6 remediation workflows operational
- ✅ Performance baselines established
- ✅ Full harness run <4 hours

---

## API Reference

### Get Device Configuration
```python
from device_matrix import get_device, get_timeout_seconds

device = get_device("pi-small")
print(device.memory_mb)  # 2000
print(device.description)  # "Raspberry Pi 2GB constrained..."

# Adjust timeout for device
timeout = get_timeout_seconds(5, "pi-small")  # 5 * 2.5 = 12.5s
```

### Get Command Configuration
```python
from command_matrix import get_command, get_command_suite, get_commands_by_tier

cmd = get_command("holdings")
print(cmd.timeout_seconds)  # 5
print(cmd.requires_portfolio)  # True

# Get all commands up to Tier 2
suite = get_command_suite(2)  # Returns 20 commands

# Get only Tier 2 commands
tier2 = get_commands_by_tier(2)  # Returns 10 commands
```

### Get Provider Configuration
```python
from provider_matrix import get_provider, is_local_provider

provider = get_provider("xai")
print(provider.model_id)  # "grok-4.1"
print(provider.supports_tool_use)  # True

# Check if local (no API key needed)
is_local = is_local_provider("gemma")  # True
```

### Remediation Workflows
```python
from remediation import RemediationWorkflow, TestFailure, FailureClass

remediation = RemediationWorkflow(max_retries=3)

# Automatic recovery
success = await remediation.execute_with_remediation(test_function)

# Get remediation log
log = remediation.get_remediation_log()
for action in log:
    print(f"{action['cap']}: {action['action']}")
```

---

## Current Test Status

### Working ✅
- Device matrix selection (mac-dev-host, pi-large, pi-small)
- Command definitions and tiers
- Timeout scaling per device
- Remediation workflows (CAP1-CAP6)
- Contract preservation system (T0-T5)

### In Development ⏳
- Provider matrix client implementations
- Full command suite testing (22 commands)
- Performance baseline establishment
- LLM provider matrix validation

### Estimated Completion
**2026-04-28** (10 business days for full v8.0 parity)

---

## Questions or Issues?

See `V11_RESTORATION_PLAN.md` for complete implementation details and roadmap.
