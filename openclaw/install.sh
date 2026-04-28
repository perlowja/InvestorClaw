#!/bin/bash
#
# InvestorClaw OpenClaw Skill Installer
# Installs InvestorClaw as an OpenClaw skill
#
# Usage:
#   curl -sSL https://gitlab.com/argonautsystems/InvestorClaw/-/raw/main/openclaw/install.sh | bash
#
# Copyright 2026 InvestorClaw Contributors
# Licensed under Apache License 2.0

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

REPO="${INVESTORCLAW_REPO_URL:-https://gitlab.com/argonautsystems/InvestorClaw.git}"
REPO_BRANCH="${INVESTORCLAW_REPO_BRANCH:-main}"
SKILL_DIR="${INVESTORCLAW_SKILL_DIR:-$HOME/.openclaw/workspace/skills/investorclaw}"
PORTFOLIO_DIR="${INVESTORCLAW_PORTFOLIO_DIR:-$HOME/portfolios}"
CLONE_DIR="/tmp/investorclaw-install-$$"
ENV_FILE="$SKILL_DIR/.env"

cleanup() {
    rm -rf "$CLONE_DIR"
}
trap cleanup EXIT

echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║          InvestorClaw OpenClaw Skill Installer v2.6.0         ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check prerequisites
echo -e "${YELLOW}[1/6]${NC} Checking prerequisites..."
if ! command -v git &> /dev/null; then
    echo -e "${RED}✗ git not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Prerequisites OK${NC}"
echo ""

# Clone repository
echo -e "${YELLOW}[2/6]${NC} Cloning from GitLab..."
if ! git clone --depth 1 --branch "$REPO_BRANCH" "$REPO" "$CLONE_DIR"; then
    echo -e "${RED}✗ Failed to clone repository${NC}"
    exit 1
fi
COMMIT_SHA=$(cd "$CLONE_DIR" && git rev-parse --short HEAD)
echo -e "${GREEN}✓ Cloned (commit: $COMMIT_SHA)${NC}"
echo ""

# Install skill
echo -e "${YELLOW}[3/6]${NC} Installing skill..."
mkdir -p "$(dirname "$SKILL_DIR")"
rm -rf "$SKILL_DIR"
if command -v rsync &> /dev/null; then
    rsync -av --exclude-from="$CLONE_DIR/.skillignore" "$CLONE_DIR/" "$SKILL_DIR/"
else
    # Fallback for minimal hosts without rsync: copy first, then remove every
    # .skillignore path/pattern so strict validators see the same curated tree.
    cp -r "$CLONE_DIR" "$SKILL_DIR"
    while IFS= read -r pattern || [ -n "$pattern" ]; do
        pattern="${pattern%%#*}"
        pattern="${pattern#"${pattern%%[![:space:]]*}"}"
        pattern="${pattern%"${pattern##*[![:space:]]}"}"
        [ -z "$pattern" ] && continue

        case "$pattern" in
            */)
                trimmed="${pattern%/}"
                if [[ "$trimmed" == */* ]]; then
                    rm -rf "$SKILL_DIR/$trimmed"
                else
                    find "$SKILL_DIR" -type d -name "$trimmed" -prune -exec rm -rf {} +
                fi
                ;;
            */*)
                rm -rf "$SKILL_DIR/$pattern"
                ;;
            *'*'*|*'?'*)
                find "$SKILL_DIR" -name "$pattern" -exec rm -rf {} +
                ;;
            *)
                rm -rf "$SKILL_DIR/$pattern"
                find "$SKILL_DIR" -name "$pattern" -exec rm -rf {} +
                ;;
        esac
    done < "$CLONE_DIR/.skillignore"
fi

if [ ! -f "$SKILL_DIR/pyproject.toml" ] || [ ! -f "$SKILL_DIR/SKILL.md" ]; then
    echo -e "${RED}✗ Installation failed: pyproject.toml or SKILL.md not found at $SKILL_DIR${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Skill installed at $SKILL_DIR${NC}"
echo ""

# Install uv + managed Python + sync dependencies + expose CLI on PATH
echo -e "${YELLOW}[4/6]${NC} Installing uv, managed Python, and syncing dependencies..."
if ! command -v uv &> /dev/null; then
    echo "  uv not found — installing via https://astral.sh/uv/install.sh ..."
    if ! curl -LsSf https://astral.sh/uv/install.sh | sh; then
        echo -e "${RED}✗ uv install failed${NC}"
        exit 1
    fi
    export PATH="$HOME/.local/bin:$PATH"
    hash -r 2>/dev/null || true
fi
if ! command -v uv &> /dev/null; then
    echo -e "${RED}✗ uv still not on PATH after install — add \$HOME/.local/bin to PATH manually${NC}"
    exit 1
fi
echo "  uv: $(uv --version)"

# Pin a managed Python interpreter — pyproject.toml + .python-version both
# specify 3.13. This avoids silent fallback to whatever system Python the
# host happened to have (e.g. some hosts only had 3.10, masking 3.11+
# feature usage like asyncio.timeout). Read .python-version from the
# clone source (it's filtered out of the curated skill subset by
# .skillignore so it won't be present in $SKILL_DIR).
PINNED_PY="$(cat "$CLONE_DIR/.python-version" 2>/dev/null | tr -d '\n' | tr -d ' ' || echo "3.13")"
echo "  Installing managed Python $PINNED_PY ..."
if ! uv python install "$PINNED_PY"; then
    echo -e "${RED}✗ uv python install $PINNED_PY failed${NC}"
    exit 1
fi

# Put the virtualenv OUTSIDE the skill directory so strict skill validators
# (ZeroClaw) don't reject the install for containing .venv symlinks. The
# default UV behavior is to create .venv inside the project; we override
# via UV_PROJECT_ENVIRONMENT so .venv lives in $HOME/.cache/investorclaw/.
VENV_DIR="${INVESTORCLAW_VENV_DIR:-$HOME/.cache/investorclaw/.venv}"
mkdir -p "$(dirname "$VENV_DIR")"

# --frozen enforces uv.lock reproducibility (matches CI behavior)
if ! (cd "$SKILL_DIR" && UV_PROJECT_ENVIRONMENT="$VENV_DIR" uv sync --frozen); then
    echo -e "${RED}✗ uv sync --frozen failed in $SKILL_DIR${NC}"
    exit 1
fi
mkdir -p "$HOME/.local/bin"
ln -sf "$VENV_DIR/bin/investorclaw" "$HOME/.local/bin/investorclaw"
if "$HOME/.local/bin/investorclaw" --version > /dev/null 2>&1; then
    echo -e "${GREEN}✓ investorclaw CLI ready: $($HOME/.local/bin/investorclaw --version 2>&1 | head -1)${NC}"
else
    echo -e "${YELLOW}⚠ CLI installed but --version probe failed (check $VENV_DIR)${NC}"
fi
echo ""

# Setup portfolio directory
echo -e "${YELLOW}[5/6]${NC} Setting up portfolio directory..."
mkdir -p "$PORTFOLIO_DIR"
echo -e "${GREEN}✓ Portfolio directory ready: $PORTFOLIO_DIR${NC}"
echo ""

# Setup .env
echo -e "${YELLOW}[6/6]${NC} Setting up configuration..."
if [ ! -f "$ENV_FILE" ]; then
    cat > "$ENV_FILE" << 'ENVFILE'
# InvestorClaw configuration for OpenClaw
# See .env.example in the skill root for the full reference.

# Portfolio paths
INVESTOR_CLAW_PORTFOLIO_DIR=~/portfolios
INVESTOR_CLAW_REPORTS_DIR=~/portfolio_reports

# Narrative synthesis — fleet default: MiniMax via Together AI
INVESTORCLAW_NARRATIVE_PROVIDER=openai_compat
INVESTORCLAW_NARRATIVE_ENDPOINT=https://api.together.xyz/v1
INVESTORCLAW_NARRATIVE_MODEL=MiniMaxAI/MiniMax-M2.7
INVESTORCLAW_NARRATIVE_API_KEY=

# Consultation layer — fleet default: Gemma 4 via the same cloud provider as
# narrative (Together AI hosts `google/gemma-4-31B-it`). Google AI Studio
# also serves `gemma-4-31b-it` directly under their generative API if you've
# set the narrative provider to google instead — switch the ENDPOINT below
# to https://generativelanguage.googleapis.com/v1beta in that case.
#
# OPTIONAL local backend: any OpenAI-compatible server (llama.cpp's
# llama-server with `--alias gemma4-consult`, ollama, vLLM, etc.) is a
# drop-in. Uncomment the LOCAL block below if you've stood one up; otherwise
# the cloud default is what fresh installs use.
INVESTORCLAW_CONSULTATION_ENABLED=true
INVESTORCLAW_CONSULTATION_ENDPOINT=https://api.together.xyz/v1
INVESTORCLAW_CONSULTATION_MODEL=google/gemma-4-31B-it
# LOCAL alternative — uncomment + adjust ENDPOINT to your local server:
#   INVESTORCLAW_CONSULTATION_ENDPOINT=http://localhost:8080
#   INVESTORCLAW_CONSULTATION_MODEL=gemma4-consult

# Provider API keys (set the one for your chosen provider)
TOGETHER_API_KEY=
# GOOGLE_API_KEY=

# Market-data keys (optional; yfinance fallback works without any)
# FINNHUB_KEY=
# NEWSAPI_KEY=
# FRED_API_KEY=
# MASSIVE_API_KEY=
# ALPHA_VANTAGE_KEY=

INVESTORCLAW_CARD_FORMAT=json
INVESTORCLAW_DEPLOYMENT_MODE=single_investor
ENVFILE
    chmod 600 "$ENV_FILE"
    echo -e "${GREEN}✓ Created .env template at $ENV_FILE${NC}"
    echo -e "${YELLOW}  Edit $ENV_FILE and add API keys. See .env.example for the full reference.${NC}"
else
    echo -e "${GREEN}✓ .env already exists at $ENV_FILE${NC}"
fi
echo ""

echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║ ✅ InvestorClaw Installation Complete                         ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "📍 Installation Details:"
echo "   Location: $SKILL_DIR"
echo "   Commit: $COMMIT_SHA"
echo "   Config: $ENV_FILE"
echo "   Portfolios: $PORTFOLIO_DIR"
echo ""
echo "🚀 Next Steps:"
echo "   1. Edit $ENV_FILE and add API keys"
echo "   2. Add portfolio CSV files to $PORTFOLIO_DIR"
echo "   3. Ensure \$HOME/.local/bin is on PATH (add to ~/.bashrc / ~/.zshrc if missing)"
echo "   4. Run: openclaw agent -m '/portfolio ask \"What is in my portfolio?\"'"
echo "   5. Refresh when needed: openclaw agent -m '/portfolio refresh'"
echo ""
echo ""
echo "⚠️  IMPORTANT: InvestorClaw is an educational analysis tool, NOT financial advice."
echo "   Consult a qualified financial advisor before making investment decisions."
echo ""
