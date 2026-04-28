# InvestorClaw Setup Scripts

This directory contains helper scripts for InvestorClaw installation and configuration.

## `setup-orchestrator`

**Fully automated environment setup for Claude Code and OpenClaw users.**

### What it does

- ✅ Detects if `uv` is installed; auto-installs if needed (~3-10s)
- ✅ Clones InvestorClaw repository from GitHub (if not present)
- ✅ Creates isolated Python virtual environment with `uv sync`
- ✅ Installs all Python dependencies (~30-45s)
- ✅ Runs portfolio setup wizard (auto-discovers broker CSV/XLS/PDF files)
- ✅ Configures environment and verifies installation

### Usage

Claude Code invokes this helper as `setup-orchestrator` from the installed
plugin `bin/` directory. Standalone developers can run it from a checkout:

```bash
bash ./bin/setup-orchestrator
```

### Platform Support

- ✅ **macOS** (Intel + Apple Silicon)
- ✅ **Linux** (Ubuntu, Debian, etc.)
- ✅ **Windows** (via WSL2)

### Environment Variables

Optional configuration:
- `INVESTORCLAW_HOME` — Custom standalone checkout directory (default: `~/InvestorClaw`)
- `INVESTORCLAW_PORTFOLIO_DIR` — Custom portfolio directory (default: `~/portfolios`)

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | uv installation failed |
| 2 | Git clone failed |
| 3 | uv sync failed (dependencies) |
| 4 | Setup wizard failed (non-fatal) |

### Typical Output

```
→ InvestorClaw Setup Orchestrator (Detected: macOS)
→ Checking for uv...
✓ uv is installed (uv 0.5.10)
→ Checking for InvestorClaw repository...
✓ Repository found at $INVESTORCLAW_HOME
→ Setting up virtual environment with uv...
✓ Dependencies installed
→ Verifying installation...
✓ InvestorClaw ready (investorclaw 2.0.0)
→ Checking for existing portfolio...
✓ Portfolio configuration found

✓ Setup complete!

Next steps:
  1. Activate environment: source $INVESTORCLAW_HOME/.venv/bin/activate
  2. Analyze portfolio: investorclaw ask "What's in my portfolio?"
  3. Refresh stale data: investorclaw refresh

For Claude Code users:
  Use InvestorClaude's natural-language surface; this adapter exposes ask/refresh.
```

### When It's Used

- **Claude Code skill activation**: `investorclaw-setup` skill invokes this automatically
- **Manual setup**: User can run directly if needed
- **CI/CD**: Can be used in automated deployment pipelines

### Dependencies

- `curl` — for downloading uv installer
- `git` — for cloning the repository
- `bash` — for script execution
- No Python requirement (uv bootstraps everything)

### Troubleshooting

**curl: command not found**
- Install curl, then rerun `setup-orchestrator`

**git: command not found**
- Install git or provide the repository manually (clone from GitHub)

**Network connectivity**
- Script requires internet access for uv download and repo clone
- Firewalls may block access to astral.sh or github.com

**Permission denied**
- Ensure the script is executable: `chmod +x setup-orchestrator`

---

## `install-investorclaw`

**Legacy: Direct pip-based installation helper (fallback method).**

Used when uv is unavailable or user prefers standard pip workflow.

```bash
install-investorclaw
```

This helper is retained only as a narrow fallback wrapper for environments that
cannot run the full orchestrator. Claude Code documentation should direct users
to `/plugin marketplace add`, `/plugin install`, and `setup-orchestrator`.

**Note**: `setup-orchestrator` is preferred for most users because it:
- Handles `uv` automatically
- Creates isolated venv (no system pollution)
- Manages Python version correctly
- Works cross-platform without homebrew

---

## Adding New Scripts

When adding new helper scripts to this directory:

1. Add `#!/bin/bash` shebang (or appropriate interpreter)
2. Make executable: `chmod +x script-name`
3. Document in this README with:
   - What it does
   - How to use it
   - Exit codes
   - Dependencies
4. Add corresponding test in `tests/test_setup_scripts.py` if relevant
5. Update `investorclaw-setup` skill if it's user-facing
