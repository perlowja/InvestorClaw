#!/bin/bash
# InvestorClaw Hermes Agent Installer
#
# Installs InvestorClaw as a skill inside the Hermes Agent runtime
# (https://github.com/NousResearch/hermes-agent — the agentic CLI; not
# to be confused with the Hermes LLM family, a separate NousResearch
# product). Optional local model backends (Ollama / vLLM / llama-server)
# are configured separately via the agent's provider selection; see
# hermes/README.md § "Local model backends" for examples.
#
# Usage:
#   bash <(curl -sSL https://gitlab.com/argonautsystems/InvestorClaw/-/raw/main/hermes/install.sh)
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
INSTALL_DIR="${INVESTORCLAW_HOME:-$HOME/InvestorClaw}"
CLONE_DIR="/tmp/investorclaw-install-$$"

cleanup() {
    rm -rf "$CLONE_DIR"
}
trap cleanup EXIT

echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   InvestorClaw Skill for Hermes Agent                         ║${NC}"
echo -e "${GREEN}║   (local model backend: Ollama / vLLM / llama-server)         ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Detect available local model backend. Hermes Agent itself is the runtime;
# the backends below serve models over OpenAI-compatible HTTP so the agent
# can reach them. Cloud providers (OpenAI / Together / xAI / Anthropic /
# OpenRouter / Nous Portal / etc.) are configured by the agent directly and
# don't need to be detected here.
log_info "Detecting local model backends..."
INFERENCE_ENGINE=""

if command -v ollama &>/dev/null; then
    INFERENCE_ENGINE="ollama"
    log_success "Ollama detected (will serve models at localhost:11434)"
elif command -v vllm &>/dev/null; then
    INFERENCE_ENGINE="vllm"
    log_success "vLLM detected"
elif command -v llama-server &>/dev/null; then
    INFERENCE_ENGINE="llama-server"
    log_success "llama-server (llama.cpp) detected"
else
    log_warn "No local model backend detected. Installing Ollama..."

    # Install Ollama
    if [ "$(uname)" = "Darwin" ]; then
        log_info "Downloading Ollama for macOS..."
        curl -LsSf https://ollama.ai/download/Ollama-darwin.zip -o /tmp/ollama.zip
        unzip /tmp/ollama.zip -d /Applications/
        rm /tmp/ollama.zip
    elif [ "$(uname)" = "Linux" ]; then
        log_info "Installing Ollama via script..."
        curl -fsSL https://ollama.ai/install.sh | sh
    else
        log_error "Unsupported OS for Ollama. Please install manually from https://ollama.ai"
        exit 1
    fi

    INFERENCE_ENGINE="ollama"
    log_success "Ollama installed"
fi

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
mv "$CLONE_DIR" "$INSTALL_DIR"
log_success "Installed to $INSTALL_DIR"

# Create directories
mkdir -p "$HOME/portfolios"
mkdir -p "$HOME/.investorclaw"
log_success "Created portfolio & config directories"

# Create skill-local .env (canonical path)
ENV_FILE="$INSTALL_DIR/.env"
log_info "Creating InvestorClaw configuration at $ENV_FILE ..."
if [ ! -f "$ENV_FILE" ]; then
    cat > "$ENV_FILE" << ENVFILE
# InvestorClaw configuration for Hermes Agent
# See .env.example in the skill root for the full reference.

# Portfolio paths
INVESTOR_CLAW_PORTFOLIO_DIR=~/portfolios
INVESTOR_CLAW_REPORTS_DIR=~/portfolio_reports

# Narrative synthesis — fleet default: MiniMax via Together AI
# Hermes Agent does not have a native Together provider; the skill reaches
# Together over its OpenAI-compatible HTTP client using the key below.
INVESTORCLAW_NARRATIVE_PROVIDER=openai_compat
INVESTORCLAW_NARRATIVE_ENDPOINT=https://api.together.xyz/v1
INVESTORCLAW_NARRATIVE_MODEL=MiniMaxAI/MiniMax-M2.7
INVESTORCLAW_NARRATIVE_API_KEY=

# Consultation layer — fleet default: Gemma 4 via the same cloud provider as
# narrative (Together AI hosts `google/gemma-4-31B-it`; Google AI Studio
# serves `gemma-4-31b-it` directly under generativelanguage.googleapis.com).
# Edge / offline deployments can point at a local llama.cpp / ollama server
# below; the cloud default is what fresh installs use.
INVESTORCLAW_CONSULTATION_ENABLED=true
INVESTORCLAW_CONSULTATION_ENDPOINT=https://api.together.xyz/v1
INVESTORCLAW_CONSULTATION_MODEL=google/gemma-4-31B-it
# LOCAL alternative — uncomment + adjust ENDPOINT to your local server:
#   INVESTORCLAW_CONSULTATION_ENDPOINT=http://localhost:8080
#   INVESTORCLAW_CONSULTATION_MODEL=gemma4-consult

# Local backend alternative (detected: $INFERENCE_ENGINE)
# Uncomment and adjust if you want fully offline operation:
#   INVESTORCLAW_NARRATIVE_ENDPOINT=http://localhost:11434/v1
#   INVESTORCLAW_NARRATIVE_MODEL=<your-local-model>

# Provider API keys
TOGETHER_API_KEY=
# GOOGLE_API_KEY=

# Market-data keys (optional)
# FINNHUB_KEY=
# NEWSAPI_KEY=
# FRED_API_KEY=

INVESTORCLAW_CARD_FORMAT=json
INVESTORCLAW_DEPLOYMENT_MODE=single_investor
ENVFILE
    chmod 600 "$ENV_FILE"
    log_success "Created $ENV_FILE (mode 600)"
else
    log_success ".env already exists at $ENV_FILE"
fi

# Run setup orchestrator
echo ""
log_info "Running setup orchestrator..."
if bash "$INSTALL_DIR/bin/setup-orchestrator"; then
    log_success "Setup complete"
else
    log_warn "Setup had issues, but installation may still work"
fi

# Start inference engine if needed
echo ""
log_info "Starting inference engine..."
case "$INFERENCE_ENGINE" in
    ollama)
        if pgrep -q ollama; then
            log_success "Ollama already running"
        else
            log_warn "Starting Ollama daemon..."
            ollama serve &
            sleep 3

            log_info "Pulling Hermes model..."
            ollama pull hermes3:8b-q4_K_M || log_warn "Model pull may require manual action"
        fi
        ;;
    hermes)
        log_success "Hermes available, ready to use"
        ;;
    vllm)
        log_warn "vLLM requires manual startup"
        echo "   Start with: python -m vllm.entrypoints.openai.api_server --model hermes-3-8b-q4"
        ;;
esac

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✅ InvestorClaw + Local Inference Ready                      ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "📍 Configuration:"
echo "   Engine: $INFERENCE_ENGINE"
echo "   Config: $ENV_FILE"
echo "   Endpoint: see INVESTORCLAW_*_ENDPOINT in $ENV_FILE"
echo ""
echo "🚀 Quick Start:"
echo "   source $INSTALL_DIR/.venv/bin/activate"
echo "   investorclaw ask \"What's in my portfolio?\""
echo "   investorclaw refresh   # force a fresh deterministic run"
echo ""
echo "💡 Privacy:"
echo "   Portfolio parsing runs locally"
echo "   Default narrative/consultation endpoints may call configured network services"
echo "   For offline operation, set local endpoints in $ENV_FILE"
echo ""
echo ""
echo "⚠️  IMPORTANT: InvestorClaw is an educational analysis tool, NOT financial advice."
echo "   Consult a qualified financial advisor before making investment decisions."
echo ""
