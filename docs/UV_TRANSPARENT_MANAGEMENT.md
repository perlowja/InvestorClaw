# Transparent uv Virtual Environment Management

**Status**: Automatic, transparent to end users  
**Version**: 2.0.0+  
**Platform Support**: macOS, Linux, Windows

---

## Overview

InvestorClaw automatically manages Python virtual environments and dependencies using `uv`. **Users don't need to run `uv sync` manually** — the system handles it completely transparently.

## How It Works

### Automatic Initialization (On First Run)

When a user runs `investorclaw` for the first time:

1. **Venv Detection** — System checks if running in a virtual environment
2. **uv Check** — Verifies if `uv` is installed; installs if missing
3. **Venv Creation** — Creates `.venv/` in project root (once)
4. **Dependency Sync** — Runs `uv sync` to install/update packages
5. **Command Execution** — User's command runs in the venv

All of this happens **silently in the background**. User just sees:

```bash
$ investorclaw holdings
# (venv auto-setup happens here, transparently)
Portfolio Summary
...
```

### Subsequent Runs

After initial setup, subsequent runs are **instant** — the venv is already initialized:

```bash
$ investorclaw portfolio list
# venv already ready, command runs immediately
{
  "portfolios": [...],
  ...
}
```

## Architecture

### Components

**`config/venv_manager.py`** — Core venv management
- `ensure_venv()` — Transparent setup: check → create → sync
- `is_venv_active()` — Detect if currently in venv
- `is_venv_initialized()` — Check if `.venv/` exists
- `sync_dependencies()` — Run `uv sync`
- `run_in_venv()` — Execute commands in venv Python

**`investorclaw`** — Installed entry point integration
- Auto-calls `ensure_venv()` before command routing
- Transparent error handling (continues if setup fails)

**`claude/bin/uv-sync`** — Optional manual sync (for advanced users)
- `./claude/bin/uv-sync sync` — Sync dependencies
- `./claude/bin/uv-sync upgrade` — Upgrade packages
- `./claude/bin/uv-sync clean` — Clean and resync

## User Experience

### First-Time Setup

```bash
$ investorclaw holdings

# [Behind the scenes]
# → Checking for uv... (installed)
# → Creating virtual environment...
# → Syncing dependencies... (30-60 seconds first run)
# → Running command in venv...

# [User sees]
Portfolio Summary
  Total Value: $39,462.00
  ...
```

### Daily Usage

```bash
$ investorclaw holdings
# Instant — venv already ready
Portfolio Summary
  ...
```

## Virtual Environment Location

Default: `~/.venv/` in project root

```
InvestorClaw/
├── .venv/                 (auto-created, ignored in git)
│   ├── bin/
│   │   ├── python
│   │   ├── investorclaw
│   │   └── ...
│   └── lib/
│       └── python3.10/
├── investorclaw
├── pyproject.toml
├── uv.lock
└── ...
```

## Dependency Management

### Locked Dependencies

`uv.lock` contains the **exact versions** of all 137 packages and their transitive dependencies. This ensures:

- ✅ **Reproducible builds** — Every user gets identical packages
- ✅ **No version conflicts** — Dependencies are pre-resolved
- ✅ **Fast installation** — No resolution step on first run
- ✅ **Offline capability** — Once synced, can run offline

### Adding New Dependencies

When adding new packages:

1. Update `requirements.txt` or `pyproject.toml`
2. Next run of `investorclaw` auto-syncs
3. Or manually: `./claude/bin/uv-sync upgrade`

Example:

```bash
# Add package to requirements.txt
echo "new-package>=1.0.0" >> requirements.txt

# Next investorclaw command auto-syncs
$ investorclaw holdings
# (uv sync runs automatically)
```

## Advanced: Manual Sync (Optional)

For power users who want explicit control:

```bash
# Sync dependencies (same as automatic)
./claude/bin/uv-sync sync

# Upgrade all packages to latest
./claude/bin/uv-sync upgrade

# Clean and resync (useful if .venv is corrupted)
./claude/bin/uv-sync clean

# Help
./claude/bin/uv-sync help
```

## Troubleshooting

### Issue: "uv: command not found"

**Cause**: uv not installed, and auto-installation failed (rare)

**Solution**: 
```bash
# Manual install (one-time)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Then retry
investorclaw holdings
```

### Issue: Venv corrupted or out of sync

**Solution**:
```bash
# Clean and resync
./claude/bin/uv-sync clean

# Or manually
rm -rf .venv
investorclaw holdings  # Auto-recreates
```

### Issue: Changes to `requirements.txt` not picked up

**Solution**:
```bash
# Force sync
./claude/bin/uv-sync upgrade

# Or wait for next command (auto-syncs on startup)
investorclaw holdings
```

## Design Philosophy

### Why Transparent?

Users shouldn't need to understand virtual environments or `uv`. They just want to run `investorclaw` and have it work.

### Why Auto-Manage?

- **Zero friction** — No setup steps
- **Correct by default** — Venv is always ready
- **Self-healing** — Detects and fixes missing dependencies
- **Educational** — New users learn by doing, not by reading docs

### Why uv?

- **Fast** — Resolves dependencies in 100ms (vs pip's 30+ seconds)
- **Reliable** — Single lock file, no version conflicts
- **Modern** — Designed for modern Python packaging
- **Cross-platform** — Works on macOS, Linux, Windows (via WSL)

## Security

### Lock File Integrity

`uv.lock` is committed to git and **must not be manually edited**. It's auto-generated by `uv sync` based on `pyproject.toml`.

```bash
# ✅ Correct way to add dependency
echo "new-package>=1.0.0" >> requirements.txt
./claude/bin/uv-sync

# ❌ Wrong way (don't edit lock file)
# vim uv.lock  # DON'T DO THIS
```

### Virtual Environment Isolation

Each user's `.venv` is **isolated and independent**:
- No system Python pollution
- No conflicts with other projects
- Safe to delete and recreate

## CI/CD Integration

For CI/CD pipelines:

```bash
# In CI/CD script
uv sync                    # Install exact versions from uv.lock
investorclaw ... # Run via the installed entrypoint in the managed venv
```

The lock file ensures reproducible builds across all environments.

## Migration from Manual pip

If users were previously using `pip install -r requirements.txt`:

- **No migration needed** — InvestorClaw auto-detects and converts
- First run of `investorclaw` automatically sets up `uv`
- Old `pip` virtual environment can be deleted

```bash
# Old way (no longer needed)
pip install -r requirements.txt

# New way (automatic)
investorclaw holdings  # Auto-creates and syncs
```

## Future Enhancements

Potential improvements:

1. **Auto-upgrade on weekly schedule** — Background dependency updates
2. **Selective syncing** — Skip sync if `uv.lock` unchanged
3. **Local-only mode** — Offline installation from cached wheels
4. **Container integration** — Docker/Podman venv snapshots
5. **Analytics** — Track setup time and dependency resolution metrics

---

## Summary

**For Users:**
- ✅ Run `investorclaw` normally
- ✅ Everything "just works"
- ✅ No manual `uv sync` needed
- ✅ Optional `./claude/bin/uv-sync` for advanced control

**For Developers:**
- ✅ Reproducible builds via `uv.lock`
- ✅ Fast, locked dependency resolution
- ✅ Easy to add new packages (`requirements.txt` + auto-sync)
- ✅ Self-healing virtual environment
