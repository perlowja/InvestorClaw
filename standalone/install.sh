#!/bin/bash
# InvestorClaw Standalone Installer
# For local development without Claude Code or OpenClaw
#
# Usage:
#   bash <(curl -sSL https://gitlab.com/argonautsystems/InvestorClaw/-/raw/main/standalone/install.sh)
#
# Copyright 2026 InvestorClaw Contributors
# Licensed under Apache License 2.0

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${YELLOW}→${NC} $1"; }
log_success() { echo -e "${GREEN}✓${NC} $1"; }
log_error() { echo -e "${RED}✗${NC} $1"; }

REPO="${INVESTORCLAW_REPO_URL:-https://gitlab.com/argonautsystems/InvestorClaw.git}"
INSTALL_DIR="${INVESTORCLAW_HOME:-$HOME/InvestorClaw}"
CLONE_DIR="/tmp/investorclaw-install-$$"

cleanup() {
    rm -rf "$CLONE_DIR"
}
trap cleanup EXIT

echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     InvestorClaw Standalone Installer (Local Development)     ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check prerequisites
log_info "Checking prerequisites..."
if ! command -v git &>/dev/null; then
    log_error "git not found. Please install git first."
    exit 1
fi
log_success "git is available"

# Clone repository
log_info "Cloning repository..."
if ! git clone --depth 1 "$REPO" "$CLONE_DIR" 2>/dev/null; then
    log_error "Failed to clone repository"
    exit 1
fi
COMMIT=$(cd "$CLONE_DIR" && git rev-parse --short HEAD)
log_success "Cloned from $REPO (commit: $COMMIT)"

# Install to target directory
log_info "Installing to $INSTALL_DIR..."
if [ -d "$INSTALL_DIR" ]; then
    log_info "Directory already exists, updating..."
    rm -rf "$INSTALL_DIR"
fi
mv "$CLONE_DIR" "$INSTALL_DIR"
log_success "Installed to $INSTALL_DIR"

# Create portfolio directory
mkdir -p "$HOME/portfolios"
mkdir -p "$HOME/.investorclaw"
log_success "Created portfolio directory: $HOME/portfolios"

# Run setup orchestrator
echo ""
log_info "Running automated setup..."
if bash "$INSTALL_DIR/bin/setup-orchestrator"; then
    log_success "Setup complete!"
else
    log_error "Setup failed"
    exit 1
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║             ✅ InvestorClaw is Ready                           ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "📍 Installation Details:"
echo "   Location: $INSTALL_DIR"
echo "   Portfolios: $HOME/portfolios"
echo "   Config: $HOME/.investorclaw/.env"
echo ""
echo "🚀 Quick Start:"
echo "   source $INSTALL_DIR/.venv/bin/activate"
echo "   investorclaw ask \"What's in my portfolio?\""
echo "   investorclaw refresh   # force a fresh deterministic run"
echo ""
echo "📚 Documentation:"
echo "   README: $INSTALL_DIR/README.md"
echo "   QUICKSTART: $INSTALL_DIR/QUICKSTART.md"
echo ""
echo ""
echo "⚠️  IMPORTANT: InvestorClaw is an educational analysis tool, NOT financial advice."
echo "   Consult a qualified financial advisor before making investment decisions."
echo ""
