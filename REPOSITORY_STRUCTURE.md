# InvestorClaw — Repository Structure & Distribution

> ⚠️ **STALE — describes pre-v2.3.0 monorepo layout.** As of v2.3.0 (Phase 2
> of IC_DECOMPOSITION) the Python engine moved to
> [`gitlab.com/argonautsystems/ic-engine`](https://gitlab.com/argonautsystems/ic-engine);
> as of v2.3.1 (Phase 3.5) the Claude Code plugin moved to
> [`gitlab.com/argonautsystems/InvestorClaude`](https://gitlab.com/argonautsystems/InvestorClaude).
> The directory trees and size numbers below predate that split. Updated
> structure documentation tracked as a follow-up; for the current shape
> see `pyproject.toml` (deps on ic-engine + clio) and
> `docs/IC_DECOMPOSITION_SPEC.md`.

**Status**: Post-Cleanup (2026-04-19)  
**Tracked Repository Size**: 8.6 MB (reduced from 11 MB)  
**Skill Payload Size**: ~240 KB  
**Buildout Time**: 2-3 minutes (uv sync)

---

## Three Distributions

### 1. Claude Code Skill Payload (~240 KB)
**What Gets Installed**: `/plugin install investorclaw@investorclaude` from the [InvestorClaude](https://gitlab.com/argonautsystems/InvestorClaude) repo (Claude Code plugin lives there, not here)

```
claude/
├── commands/          # Slash command definitions (/investorclaw:ic-holdings, etc.)
├── skills/            # Task automation (setup, analysis, report generation)
└── README.md          # User-facing guide
```

**Size**: 240 KB (includes command specs, skill metadata)  
**Dependencies**: Inherited from main Python environment (uv sync)  
**Time to Install**: ~2 seconds (just extracts files)

---

### 2. Complete Source Distribution (GitHub/GitLab)
**What Gets Cloned**: `git clone https://gitlab.com/argonautsystems/InvestorClaw`

```
InvestorClaw/
├── claude/              # ← Skill definitions (240 KB)
├── commands/            # ← Analysis engines (1.3 MB)
├── config/              # ← Schema, CDM, builders (324 KB)
├── internal/            # ← Pipeline orchestration (360 KB)
├── rendering/           # ← Dashboard, Stonkmode (2.1 MB)
├── services/            # ← Data fetching (212 KB)
├── runtime/             # ← Router, environment (112 KB)
├── setup/               # ← Interactive setup (228 KB)
├── providers/           # ← LLM providers (128 KB)
├── models/              # ← Enterprise CDM 6.0 (180 KB, on enterprise branch)
├── harness/             # ← Test harness v11 (300 KB)
├── tests/               # ← Test suite (580 KB)
├── docs/                # ← Documentation (2.7 MB)
├── assets/              # ← Sample reports, images (2 MB)
├── requirements.txt     # ← Python dependencies
├── package.json         # ← Node.js dependencies (optional)
└── bin/          # ← Setup orchestrator scripts
```

**Size**: 8.6 MB (git-tracked source)  
**Dependencies**: 
  - Python 3.9+ (installed by uv)
  - Node.js (optional, for PWA build)
- **Time to Build**: 2-3 minutes (uv sync + npm install)

---

### 3. Development Environment (Full Disk)
**Location**: NAS NAS ONLY (not in git remotes)  
**What's on Disk**: `git clone + uv sync + npm install`

```
/mnt/nas/datapool/InvestorClaw/  (on NAS NAS)
├── [tracked files]      # ← 8.6 MB (git source, pulled from canonical GitHub remote)
├── node_modules/        # ← 1.7 GB (npm dependencies, built locally, NOT tracked)
├── .venv/               # ← ~500 MB (Python venv, built locally, NOT tracked)
└── [working files]      # ← Temporary builds, caches, coverage reports
```

**Size**: ~2.2 GB on NAS only  
**Git Remotes** (canonical: GitHub; legacy GitLab mirror retained for now): Track ONLY the 8.6 MB source  
**Exclusions** (in `.gitignore`): `node_modules/`, `.venv/`, `venv/`, `ENV/`, `env/`, `.python/`

**Important**: Development disk (.venv, node_modules, build artifacts) is built locally from requirements.txt/package.json and kept on NAS for backup/NFS access. It is NEVER pushed to public or private git remotes.

---

## What Changed (Repository Cleanup)

### Removed from Tracking
- ✅ **Lock files** (uv.lock 1.2MB, package-lock.json 404KB) — now in `.gitignore`
- ✅ **Old harnesses** — v6.11, v6.12, v7.1, v8.0, v8.1 (kept v11 only)
- ✅ **Old test runners** — harness_v10_*.py, run_harness_*.py
- ✅ **Old test scripts** — phase_bz_test_spec.sh, test_gemma_*.sh, etc.
- ✅ **Research docs** — MARKET_PREDICTION_ARCHITECTURE.md (moved to archive/)

### Result
- **Before**: 11 MB tracked (including lock files and old harnesses)
- **After**: 8.6 MB tracked (clean, current versions only)
- **Reduction**: 22% smaller distribution

---

## Skill Payload Optimization

The Claude Code skill only includes `./claude/` directory and Python dependencies:

| Component | Size | Included in Skill | Note |
|-----------|------|-------------------|------|
| Slash commands | 80 KB | ✅ Yes | Core skill functionality |
| Skills (automation) | 160 KB | ✅ Yes | Setup, analysis, report |
| Commands (analysis) | 1.3 MB | ✅ Yes (pulled by uv sync) | Holdings, performance, bonds, etc. |
| Dashboard code | 2.1 MB | ✅ Yes (pulled by uv sync) | Plotly, rendering, artifacts |
| Tests | 580 KB | ❌ No | Not shipped with skill |
| Docs | 2.7 MB | ❌ No | Available separately on GitHub |
| Assets | 2 MB | ⚠️ Partial | Images embedded in dashboard JS |
| Harness | 300 KB | ❌ No | For development/CI only |

**Actual Skill Installation**:
1. Download 240 KB (skill definitions)
2. Run `uv sync` to fetch Python dependencies (incremental, cached)
3. Run `npm install` for PWA assets (optional, cached)
4. Total deployment: ~2-3 minutes on first install

---

## Branch Distribution

### main (v2.0.0 — Open Source)
- **Size**: 8.6 MB tracked
- **CDM Version**: 5.x (stable)
- **Distribution**: GitHub, GitLab, Anthropic Marketplace
- **Contents**: Full source, tests, harness v11, docs
- **No Commercial Code**: Enterprise features on separate branch

### enterprise (v2.0.0-enterprise — Commercial)
- **Size**: main + 4 enterprise-specific commits (~50 KB additional)
- **CDM Version**: 6.0 (with 5.x compatibility via context.cdm_version)
- **Distribution**: Private git remote only (pre-push hook blocks public push)
- **Contents**: All of main + audit ledger, party hierarchies, RBAC, feature gates

---

## CI/CD Distribution

When creating CI/CD pipelines:

| Stage | Files | Size | Purpose |
|-------|-------|------|---------|
| Test (P3) | claude/, commands/, tests/ | ~2 MB | Run contract tests, verify commands |
| Build (P3) | rendering/pwa/, assets/ | ~2.5 MB | Compile dashboard PWA |
| Ship Skill | claude/ | 240 KB | Upload skill to marketplace |
| Archive Docs | docs/ | 2.7 MB | Upload to doc site separately |

---

## Best Practices (Post-Cleanup)

1. **Don't commit lock files** — added to .gitignore (uv.lock, package-lock.json, etc.)
2. **Keep only current harness** — v11 is canonical; old versions in archive/
3. **Separate source from build** — tracked source (8.6 MB) vs full disk (2.2 GB, NAS only)
4. **Skill payload is minimal** — only claude/ + runtime dependencies
5. **Clean up research docs** — move to archive/ instead of committing
6. **Development disk on NAS only** — never push .venv/ or node_modules/ to remotes
   - Clone to NAS: `/mnt/nas/datapool/InvestorClaw/`
   - Run `uv sync && npm install` locally (creates .venv and node_modules on NAS)
   - Git remotes stay clean (8.6 MB only)
7. **All remotes (.gitignore enforced)**:
   - github (canonical public): 8.6 MB source
   - gitlab (legacy public mirror): 8.6 MB source (phased out as canonical in v2.1.0; pushed for continuity only)
   - nas (private NAS bare): 8.6 MB source
   - Pre-push hook blocks `enterprise` branch from public remotes

---

## Going Forward

- **Source distribution**: 8.6 MB (main) + 50 KB (enterprise)
- **Skill payload**: ~240 KB manifest + dependencies (pulled by uv)
- **Development environment**: ~2.2 GB on disk (not tracked)
- **CI/CD stages**: Selective distribution per pipeline stage

✅ Repository is now clean and properly scoped for distribution.
