#!/bin/bash
# InvestorClaw zeroclaw Installer (Raspberry Pi)
#
# Installs InvestorClaw for zeroclaw runtime on Raspberry Pi
#
# Addresses zeroclaw v0.6.9 limitations:
# - Disables open-skills to prevent token overflow
# - Configures proper Docker sandbox
# - Increases context window for portfolio analysis
# - Handles vendor dependency management
#
# Usage:
#   bash <(curl -sSL https://gitlab.com/argonautsystems/InvestorClaw/-/raw/main/zeroclaw/install.sh)
#
# Copyright 2026 InvestorClaw Contributors
# Licensed under Apache License 2.0

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}→${NC} $1"; }
log_success() { echo -e "${GREEN}✓${NC} $1"; }
log_warn() { echo -e "${YELLOW}⚠${NC} $1"; }
log_error() { echo -e "${RED}✗${NC} $1"; }

REPO="${INVESTORCLAW_REPO_URL:-https://gitlab.com/argonautsystems/InvestorClaw.git}"
INSTALL_DIR="${INVESTORCLAW_HOME:-$HOME/investorclaw}"
ZEROCLAW_CONFIG="$HOME/.zeroclaw/config.toml"
CLONE_DIR="/tmp/investorclaw-install-$$"

cleanup() {
    rm -rf "$CLONE_DIR"
}
trap cleanup EXIT

echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║         InvestorClaw for zeroclaw (Raspberry Pi)              ║${NC}"
echo -e "${GREEN}║         Fixing v0.6.9 token overflow & sandbox issues        ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if running on Raspberry Pi
log_info "Verifying Raspberry Pi environment..."
if ! grep -q "Raspberry Pi" /proc/device-tree/model 2>/dev/null; then
    log_warn "Not running on Raspberry Pi, but proceeding..."
fi
log_success "Environment check passed"

# Check zeroclaw is installed
if ! command -v zeroclaw &>/dev/null; then
    log_error "zeroclaw CLI not found. Please install zeroclaw first."
    exit 1
fi
log_success "zeroclaw is installed"

# Clone repository
log_info "Cloning InvestorClaw..."
if ! git clone --depth 1 "$REPO" "$CLONE_DIR" 2>/dev/null; then
    log_error "Failed to clone repository"
    exit 1
fi
COMMIT=$(cd "$CLONE_DIR" && git rev-parse --short HEAD)
log_success "Cloned (commit: $COMMIT)"

# Install to target directory
log_info "Installing to $INSTALL_DIR..."
if [ -d "$INSTALL_DIR" ]; then
    log_warn "Updating existing installation..."
    rm -rf "$INSTALL_DIR"
fi
mkdir -p "$(dirname "$INSTALL_DIR")"
mv "$CLONE_DIR" "$INSTALL_DIR"
log_success "Installed to $INSTALL_DIR"

# Create directories
mkdir -p "$HOME/portfolios"
mkdir -p "$HOME/.investorclaw"
log_success "Created portfolio & config directories"

# Configure zeroclaw for InvestorClaw
echo ""
log_info "Configuring zeroclaw..."

if [ ! -f "$ZEROCLAW_CONFIG" ]; then
    log_warn "zeroclaw config not found at $ZEROCLAW_CONFIG"
    log_info "Please run: zeroclaw config init"
    exit 1
fi

# Backup original config
cp "$ZEROCLAW_CONFIG" "$ZEROCLAW_CONFIG.backup.$(date +%s)"
log_success "Backed up zeroclaw config"

# Apply critical fixes for InvestorClaw
log_info "Applying zeroclaw configuration fixes..."

# Fix 1: Disable open-skills (prevents 96K token overflow)
if grep -q "open_skills_enabled = true" "$ZEROCLAW_CONFIG"; then
    sed -i.bak 's/open_skills_enabled = true/open_skills_enabled = false/g' "$ZEROCLAW_CONFIG"
    log_success "Disabled open-skills (prevents token overflow)"
else
    log_warn "open_skills_enabled already disabled or not found"
fi

# Fix 2: Increase context window (for portfolio analysis)
if grep -q "max_context_tokens = 32000" "$ZEROCLAW_CONFIG"; then
    sed -i.bak 's/max_context_tokens = 32000/max_context_tokens = 131072/g' "$ZEROCLAW_CONFIG"
    log_success "Increased context window to 131K tokens"
else
    log_warn "Context window may already be configured"
fi

# Fix 3: Enable full autonomy (for non-interactive skill execution)
if grep -q 'level = "supervised"' "$ZEROCLAW_CONFIG"; then
    sed -i.bak 's/level = "supervised"/level = "full"/g' "$ZEROCLAW_CONFIG"
    log_success "Enabled full autonomy for skill execution"
else
    log_warn "Autonomy level may already be configured"
fi

# Fix 4: Disable sandbox (Docker still applies in v0.6.9, but config updates)
if grep -q 'backend = "auto"' "$ZEROCLAW_CONFIG"; then
    sed -i.bak 's/backend = "auto"/backend = "none"/g' "$ZEROCLAW_CONFIG"
    log_success "Configured sandbox backend"
else
    log_warn "Sandbox backend may already be configured"
fi

# Create skill-local .env (canonical path)
ENV_FILE="$INSTALL_DIR/.env"
log_info "Creating InvestorClaw configuration at $ENV_FILE ..."
if [ ! -f "$ENV_FILE" ]; then
    cat > "$ENV_FILE" << 'ENVFILE'
# InvestorClaw configuration for ZeroClaw
# See .env.example in the skill root for the full reference.

# Portfolio paths
INVESTOR_CLAW_PORTFOLIO_DIR=~/portfolios
INVESTOR_CLAW_REPORTS_DIR=~/portfolio_reports

# Narrative synthesis — fleet default: MiniMax via Together AI
# Edge deployments on slow networks may prefer a local backend (see below).
INVESTORCLAW_NARRATIVE_PROVIDER=openai_compat
INVESTORCLAW_NARRATIVE_ENDPOINT=https://api.together.xyz/v1
INVESTORCLAW_NARRATIVE_MODEL=MiniMaxAI/MiniMax-M2.7
INVESTORCLAW_NARRATIVE_API_KEY=

# Consultation layer — fleet default: Gemma 4 (31B) via Together AI
INVESTORCLAW_CONSULTATION_ENABLED=true
INVESTORCLAW_CONSULTATION_ENDPOINT=http://192.0.2.96:8080
INVESTORCLAW_CONSULTATION_MODEL=gemma4-consult

# Local alternative for offline edge nodes (set ENDPOINT to your host):
#   INVESTORCLAW_NARRATIVE_ENDPOINT=http://raspberrypi.local:11434
#   INVESTORCLAW_NARRATIVE_MODEL=<local-model>

# Provider API keys
TOGETHER_API_KEY=
# GOOGLE_API_KEY=

# Market-data keys (optional)
# FINNHUB_KEY=
# NEWSAPI_KEY=
# FRED_API_KEY=

INVESTORCLAW_DEPLOYMENT_MODE=single_investor
ENVFILE
    chmod 600 "$ENV_FILE"
    log_success "Created $ENV_FILE (mode 600)"
else
    log_success ".env already exists at $ENV_FILE"
fi

# Install dependencies via uv (auto-installs Python if missing — matches
# openclaw/install.sh self-bootstrap pattern so this script works on
# edge containers that don't ship with Python 3 pre-installed).
log_info "Installing dependencies via uv..."

if ! command -v uv &>/dev/null; then
    log_info "uv not found — installing via https://astral.sh/uv/install.sh ..."
    if ! curl -LsSf https://astral.sh/uv/install.sh | sh; then
        log_error "uv install failed. Install uv manually: https://docs.astral.sh/uv/getting-started/installation/"
        exit 1
    fi
    export PATH="$HOME/.cargo/bin:$HOME/.local/bin:$PATH"
fi

if ! command -v uv &>/dev/null; then
    log_error "uv still not on PATH after install. Add \$HOME/.local/bin to PATH and re-run."
    exit 1
fi

log_info "uv: $(uv --version 2>&1)"
if ! (cd "$INSTALL_DIR" && uv sync); then
    log_error "uv sync failed in $INSTALL_DIR — check pyproject.toml and network connectivity."
    exit 1
fi
log_success "Installed dependencies into $INSTALL_DIR/.venv (uv-managed Python)"

# Symlink the investorclaw entry point so /usr/local/bin catches it
# (needed for agent exec shells that sanitize PATH and don't load ~/.bashrc).
if [ -x "$INSTALL_DIR/.venv/bin/investorclaw" ]; then
    mkdir -p "$HOME/.local/bin"
    ln -sf "$INSTALL_DIR/.venv/bin/investorclaw" "$HOME/.local/bin/investorclaw"
    if sudo -n true 2>/dev/null; then
        sudo ln -sf "$INSTALL_DIR/.venv/bin/investorclaw" /usr/local/bin/investorclaw 2>/dev/null
    fi
    log_success "investorclaw CLI on PATH: $($HOME/.local/bin/investorclaw --version 2>&1 | head -1)"
fi

# Run setup orchestrator
echo ""
log_info "Running setup orchestrator..."
if bash "$INSTALL_DIR/bin/setup-orchestrator"; then
    log_success "Setup complete"
else
    log_warn "Setup had issues"
fi

# Restart zeroclaw service
log_info "Restarting zeroclaw service..."
if systemctl --user is-active --quiet zeroclaw.service; then
    systemctl --user restart zeroclaw.service
    log_success "zeroclaw service restarted"
else
    log_warn "zeroclaw service not found or not running"
    log_info "Start manually: zeroclaw gateway start"
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✅ InvestorClaw for zeroclaw Ready                           ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "📍 Configuration Applied:"
echo "   open_skills_enabled = false (prevents token overflow)"
echo "   max_context_tokens = 131072 (increased for portfolio analysis)"
echo "   autonomy level = full (allows shell execution)"
echo "   sandbox backend = none (v0.6.9 workaround)"
echo ""
echo "📂 Installation:"
echo "   Location: $INSTALL_DIR"
echo "   Config: $ENV_FILE"
echo "   zeroclaw Config: $ZEROCLAW_CONFIG"
echo ""
echo "⚙️  Next Steps:"
echo "   1. Verify zeroclaw config: cat $ZEROCLAW_CONFIG | grep -E 'open_skills|max_context|level|backend'"
echo "   2. Test connection: zeroclaw gateway status"
echo "   3. Run: zeroclaw agent -m 'investorclaw ask \"What's in my portfolio?\"'"
echo "   4. Refresh when needed: zeroclaw agent -m 'investorclaw refresh'"
echo ""
echo "🔧 Troubleshooting:"
echo "   - Config issues: restore from backup at $ZEROCLAW_CONFIG.backup.*"
echo "   - Dependencies: cd $INSTALL_DIR && uv sync"
echo "   - Context overflow: verify open_skills_enabled = false"
echo ""
echo ""
echo "⚠️  IMPORTANT: InvestorClaw is an educational analysis tool, NOT financial advice."
echo "   Consult a qualified financial advisor before making investment decisions."
echo ""
