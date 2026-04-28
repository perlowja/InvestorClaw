#!/bin/bash
# InvestorClaw Universal Installer
#
# One-line installation for all platforms
#
# 1-Line Commands:
#
# Claude Code (GUI):
#   Install from URL → https://gitlab.com/argonautsystems/InvestorClaw
#
# OpenClaw:
#   curl -sSL https://gitlab.com/argonautsystems/InvestorClaw/-/raw/main/install.sh | bash -s -- --platform openclaw
#
# Standalone (Local Development):
#   curl -sSL https://gitlab.com/argonautsystems/InvestorClaw/-/raw/main/install.sh | bash -s -- --platform standalone
#
# zeroclaw (Raspberry Pi):
#   curl -sSL https://gitlab.com/argonautsystems/InvestorClaw/-/raw/main/install.sh | bash -s -- --platform zeroclaw
#
# Hermes (Local Inference):
#   curl -sSL https://gitlab.com/argonautsystems/InvestorClaw/-/raw/main/install.sh | bash -s -- --platform hermes
#
# Auto-Detect:
#   curl -sSL https://gitlab.com/argonautsystems/InvestorClaw/-/raw/main/install.sh | bash
#
# Copyright 2026 InvestorClaw Contributors
# Licensed under Apache License 2.0

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${BLUE}→${NC} $1"; }
log_success() { echo -e "${GREEN}✓${NC} $1"; }
log_warn() { echo -e "${YELLOW}⚠${NC} $1"; }
log_error() { echo -e "${RED}✗${NC} $1"; }

echo ""
echo "⚠️  IMPORTANT: InvestorClaw is an educational analysis tool, NOT financial advice."
echo "   Consult a qualified financial advisor before making investment decisions."
echo ""

# Parse arguments
PLATFORM="${1:-auto}"
# Support "--platform <name>" form (when called via `bash -s -- --platform openclaw`)
if [ "$PLATFORM" = "--platform" ]; then
    PLATFORM="${2:-auto}"
fi
REPO_HOST="${INVESTORCLAW_REPO_HOST:-GitHub}"

# Detect platform if auto
if [ "$PLATFORM" = "auto" ]; then
    if command -v openclaw &>/dev/null; then
        PLATFORM="openclaw"
    elif grep -q "Raspberry Pi" /proc/device-tree/model 2>/dev/null; then
        PLATFORM="zeroclaw"
    # Hermes binary isn't shipped — only auto-detect via Ollama presence
    elif command -v ollama &>/dev/null; then
        PLATFORM="hermes"
    else
        PLATFORM="standalone"
    fi
fi

echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              InvestorClaw Universal Installer v2.0.0                  ║${NC}"
echo -e "${GREEN}║                   Platform: $PLATFORM                                      ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Delegate to platform-specific installer
case "$PLATFORM" in
    openclaw)
        log_info "Installing for OpenClaw..."
        exec bash <(curl -sSL https://gitlab.com/argonautsystems/InvestorClaw/-/raw/main/openclaw/install.sh)
        ;;
    standalone|local)
        log_info "Installing for standalone (local development)..."
        exec bash <(curl -sSL https://gitlab.com/argonautsystems/InvestorClaw/-/raw/main/standalone/install.sh)
        ;;
    zeroclaw|raspi|rpi)
        log_info "Installing for zeroclaw (Raspberry Pi)..."
        exec bash <(curl -sSL https://gitlab.com/argonautsystems/InvestorClaw/-/raw/main/zeroclaw/install.sh)
        ;;
    hermes|ollama|local-inference)
        log_info "Installing for Hermes/Ollama (local inference)..."
        exec bash <(curl -sSL https://gitlab.com/argonautsystems/InvestorClaw/-/raw/main/hermes/install.sh)
        ;;
    *)
        log_error "Unknown platform: $PLATFORM"
        echo ""
        echo "Supported platforms:"
        echo "  openclaw     - OpenClaw agent framework"
        echo "  standalone   - Local Python CLI (development)"
        echo "  zeroclaw     - Raspberry Pi / zeroclaw runtime"
        echo "  hermes       - Local Hermes/Ollama inference"
        echo "  auto         - Auto-detect (default)"
        echo ""
        echo "Usage:"
        echo "  curl -sSL https://gitlab.com/argonautsystems/InvestorClaw/-/raw/main/install.sh | bash"
        echo "  curl -sSL ... | bash -s -- --platform openclaw"
        exit 1
        ;;
esac
