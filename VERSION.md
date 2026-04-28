# InvestorClaw Version Management

**Canonical version**: `2.5.0` (defined in `pyproject.toml`).

Phase 2 of the IC_DECOMPOSITION (v2.3.0) moved the engine into a separate
package (`ic-engine`). The InvestorClaw repo is now an adapter package; its
version is the **adapter** version. The CLI version reported by
`investorclaw --version` comes from the underlying ic-engine.

## Accessing the version

```bash
# Adapter (this repo) — pyproject.toml
grep '^version' pyproject.toml

# Engine — ic-engine pyproject + __version__
python3 -c "import ic_engine; print(ic_engine.__version__)"

# CLI
investorclaw --version
```

## Bumping the version

1. Update `version = "..."` in `pyproject.toml`.
2. Update `version` in `openclaw/skill.json`.
3. Update the version in `SKILL.toml`, `openclaw/skill.json`, `openclaw.plugin.json`, `package.json`, and `investorclaw.py`.
4. Tag with `git tag -a vX.Y.Z` and push to nas + gitlab.

## Adapter vs engine versioning

The adapter and the engine version independently:

| Repo            | Versioning             | Source of truth                          |
| --------------- | ---------------------- | ---------------------------------------- |
| `InvestorClaw`  | adapter version (this) | `pyproject.toml`                         |
| `ic-engine`     | engine version         | `ic-engine/pyproject.toml` + `__version__` |
| `clio`          | foundation version     | `clio/pyproject.toml` + `__version__`    |

A new adapter release does not require an engine bump (and vice versa).
The adapter declares an engine compatibility range via the dependency pin
in `pyproject.toml` (currently `ic-engine @ git+...@v2.5.0`).
