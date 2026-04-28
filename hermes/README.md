# InvestorClaw Skill for Hermes Agent

v2.5.0 installs InvestorClaw as a skill inside the [Hermes Agent](https://github.com/NousResearch/hermes-agent) runtime. You can then ask natural-language portfolio questions through the deterministic `ic-engine` v2.5.0 pipeline against any provider that Hermes Agent supports. Cloud providers are the default; fully local models served by Ollama, llama-server, LMStudio, or vLLM are supported when you configure them explicitly.

> Naming note: *Hermes Agent* is the NousResearch agentic CLI runtime. It is analogous to OpenClaw or ZeroClaw. Claude Code support lives in the separate InvestorClaude plugin.
>
> The *Hermes LLM family* is a separate product. That family includes Hermes 3 and Hermes 4, which are NousResearch fine-tunes of Llama and Qwen.
>
> Hermes Agent can use a Hermes LLM as its backend model. It can also use any other model the agent supports.
>
> This page covers how to install the InvestorClaw *skill* into the *agent runtime*. Model choice is decoupled.

## Local Model Backends

Hermes Agent can connect to any OpenAI-compatible local inference backend. Choose one of these backends if you want fully offline operation. Otherwise, configure Hermes Agent to use a cloud provider.

| Backend | Best for | Setup | Throughput | GUI |
|---|---|---|---|---|
| Ollama | Simplicity, daemon mode | Easiest (1 command) | ~30-40 tok/s | No |
| llama-server | Production, max context | Medium | ~60-70 tok/s | No |
| LMStudio | Ease of use, model switching | Easy (click UI) | ~40-50 tok/s | Yes |
| vLLM | Max throughput, batching | Harder (Python) | ~90+ tok/s | No |

llama-server gives the best balance of context window (131K), speed, and reliability. The backend only needs to speak the OpenAI-compatible HTTP schema. Hermes Agent handles the rest.

## Quick Start

Set up a cloud provider first if you want the default path. Set up a local backend if you want fully offline operation.

### Cloud Provider Setup

This path mirrors how you use OpenClaw or ZeroClaw. Point Hermes Agent at a cloud provider and run InvestorClaw.

```bash
# 1. Install Hermes Agent (one-time; see github.com/NousResearch/hermes-agent)
#    (then run `hermes setup` for provider credentials if you haven't already)

# 2. Install InvestorClaw into Hermes Agent
curl -sSL https://gitlab.com/argonautsystems/InvestorClaw/-/raw/main/hermes/install.sh | bash

# 3. Pick a provider + model Hermes Agent supports natively
hermes model set --provider xai       --model grok-4-1-fast
#   or: --provider anthropic           --model claude-sonnet-4
#   or: --provider gemini              --model gemini-2.5-flash
#   or: --provider nvidia              --model meta/llama-3.3-70b-instruct
# For Together / Groq / OpenAI-direct / Perplexity (not native to Hermes Agent),
# reach them via OpenRouter:
#   --provider openrouter --model meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8

# 4. Use
investorclaw ask "What's in my portfolio?"
investorclaw ask "Analyze my portfolio"
```

### Fully Offline Setup

Use one of these local backends if you want zero cloud calls. Hermes Agent works with any OpenAI-compatible local model. These examples use NousResearch's Hermes 3 because it fits the Hermes Agent runtime naturally, but Qwen, Llama 3, Mistral, and other models also work.

#### Ollama

Ollama is the easiest local option.

```bash
# 1. Install Ollama (one-time)
brew install ollama  # or download from ollama.ai

# 2. Start daemon + pull a model
ollama serve &
ollama pull hermes3:8b-q4_K_M            # or: mistral:latest, llama3.1:70b, qwen2.5-coder:7b

# 3. Install InvestorClaw + point Hermes Agent at the local endpoint
curl -sSL https://gitlab.com/argonautsystems/InvestorClaw/-/raw/main/hermes/install.sh | bash
hermes model set --provider ollama-cloud --endpoint http://localhost:11434 --model hermes3:8b-q4_K_M

# 4. Use
investorclaw ask "What's in my portfolio?"
```

#### llama-server

llama-server works well for long context.

```bash
# 1. Install llama.cpp
brew install llama.cpp                       # macOS
# or: apt-get install llama-cpp-server       # Linux

# 2. Download any GGUF model (Hermes 3 used as the example; substitute freely)
wget https://huggingface.co/second-state/Hermes-3-Llama-3.1-8B-GGUF/resolve/main/Hermes-3-Llama-3.1-8B-Q6_K.gguf

# 3. Serve it
llama-server -m ./Hermes-3-Llama-3.1-8B-Q6_K.gguf -ngl 99 --ctx-size 131072 --port 8080

# 4. Install InvestorClaw + configure Hermes Agent
curl -sSL https://gitlab.com/argonautsystems/InvestorClaw/-/raw/main/hermes/install.sh | bash
hermes model set --provider openai-compat --endpoint http://localhost:8080/v1 --model local

# 5. Use
investorclaw ask "What's in my portfolio?"
```

#### LMStudio

LMStudio gives you a GUI for local models.

```bash
# 1. Download LMStudio: https://lmstudio.ai
# 2. Search + load any model (e.g., "Hermes 3 8B", "Qwen2.5-Coder-7B", "Mistral 7B")
# 3. Developer → Local Server → Start Server (default port 1234)

curl -sSL https://gitlab.com/argonautsystems/InvestorClaw/-/raw/main/hermes/install.sh | bash
hermes model set --provider openai-compat --endpoint http://localhost:1234/v1 --model local

investorclaw ask "What's in my portfolio?"
```

#### vLLM

vLLM gives you high local throughput.

```bash
pip install vllm
python -m vllm.entrypoints.openai.api_server \
  --model NousResearch/Hermes-3-Llama-3.1-8B \
  --quantization bitsandbytes \
  --gpu-memory-utilization 0.9 \
  --port 8000 &

curl -sSL https://gitlab.com/argonautsystems/InvestorClaw/-/raw/main/hermes/install.sh | bash
hermes model set --provider openai-compat --endpoint http://localhost:8000/v1 --model NousResearch/Hermes-3-Llama-3.1-8B

investorclaw ask "What's in my portfolio?"
```

## Activate and Use

Activate InvestorClaw after your local backend is running and Hermes Agent points to it.

```bash
source ~/InvestorClaw/.venv/bin/activate
investorclaw ask "What's in my portfolio?"
investorclaw ask "Give me the full picture"
investorclaw refresh       # force a fresh deterministic run
```

## Features

InvestorClaw runs inside Hermes Agent as a skill. It supports cloud-first and fully local workflows.

- InvestorClaw runs as a skill inside Hermes Agent, which is the NousResearch agentic CLI.
- Cloud-first is the default. This matches OpenClaw and ZeroClaw.
- Fully local operation is optional. You can point Hermes Agent at Ollama, llama-server, LMStudio, or vLLM.
- The v2.5.0 command surface is available. See [Commands](#commands).

Hermes Agent's provider coverage breaks down like this:

- Native `--provider` targets from `hermes chat -h` argparse:
  - `openrouter`
  - `nous`
  - `anthropic`
  - `gemini`
  - `xai`
  - `nvidia`
  - `minimax`
  - `ollama-cloud`
  - `huggingface`
  - `openai-codex` (ChatGPT-subscriber flow, distinct from OpenAI direct API)
  - `copilot`
  - `copilot-acp`
  - `zai`
  - `kimi-coding`
  - `kimi-coding-cn`
  - `stepfun`
  - `kilocode`
  - `xiaomi`
  - `arcee`
  - `minimax-cn`
- Reachable via OpenRouter proxy:
  - Together
  - Groq
  - OpenAI (direct API)
  - Perplexity
  - Most other OpenAI-compatible providers
- Config-only, not CLI-wireable yet:
  - `custom_providers:` in `~/.hermes/config.yaml` supports arbitrary OpenAI-compatible endpoints
  - `hermes chat --provider` argparse hardcodes its enum, so `custom:<slug>` is not accepted
  - Upstream bug is being tracked
  - InvestorClaw-side workaround is to use OpenRouter

> NousResearch also ships the Hermes LLM family. That family includes Hermes 3 and Hermes 4, which are fine-tunes of Llama and Qwen.
>
> These models are optional. You can run them through Ollama or the Nous Portal API.
>
> Hermes Agent does not require a Hermes-branded model. Use the provider and model that fit your workload.

## Configuration

Configure Hermes Agent once, then let InvestorClaw inherit the active provider and model for LLM-backed work. That includes narrative synthesis, Stonkmode, and consultation.

### Cloud Provider Configuration

Hermes Agent handles provider selection. Use `hermes model` or `hermes setup`.

```bash
hermes model set --provider xai --model grok-4-1-fast
hermes model set --provider openai --model gpt-5.4
hermes model set --provider together --model meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8
```

### Local Ollama Configuration

Point Hermes Agent at a local Ollama endpoint if you want offline operation.

```bash
ollama pull hermes3:8b-q4_K_M            # NousResearch's Hermes 3, if you want it
# or any other: ollama pull mistral:latest, llama3.1:70b, etc.

hermes model set --provider ollama-cloud --endpoint http://localhost:11434
```

Use these optional InvestorClaw environment variables if you want the skill to bypass Hermes Agent's provider for a specific call:

```bash
INVESTORCLAW_NARRATIVE_PROVIDER=openai_compat
INVESTORCLAW_NARRATIVE_ENDPOINT=http://localhost:11434/v1
INVESTORCLAW_NARRATIVE_MODEL=hermes3:8b-q4_K_M       # or whatever you pulled
```

### Market Data APIs

Set these variables if you want market data integrations:

```bash
FINNHUB_KEY=your_key
NEWSAPI_KEY=your_key
POLYGON_API_KEY=your_key
```

## Supported Providers and Example Models

Hermes Agent supports many providers. The table below shows a representative sample tested with InvestorClaw.

### Cloud

| Provider | Example model | Notes |
|---|---|---|
| xAI | `grok-4-1-fast` | Default cross-runtime pilot target |
| OpenAI | `gpt-5.4` | Good all-rounder |
| Together | `meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8` | High-quality open weights |
| Anthropic | `claude-sonnet-4` | Strong narrative synthesis |
| Groq | `llama-3.3-70b-versatile` | Free tier, fast |
| Nous Portal | `Hermes-4-405B` (or current flagship) | If you want to run NousResearch's own LLM family as a hosted provider |

### Local

These local options work through Ollama, llama-server, LMStudio, vLLM, or any other OpenAI-compatible endpoint.

| Model | Size | Speed | Notes |
|---|---|---|---|
| Qwen2.5-Coder-7B-Instruct | ~5 GB | Fast | Solid for tool use + code |
| Hermes 3 (8B) | 6 GB | Fast | NousResearch's own, optional |
| Hermes 4 (8B / 70B) | 6–40 GB | Fast | NousResearch's latest, optional |
| Mistral 7B / Ministral 8B | 4–5 GB | Fast | Lightweight baseline |
| Llama 3.1 70B | ~40 GB | Slower | Higher quality, higher RAM |

All of these models work with InvestorClaw's deterministic `ask` / `refresh` command set.

The default cross-runtime parity pilot uses `xai/grok-4-1-fast`. All three runtimes, OpenClaw, ZeroClaw, and Hermes Agent, support it natively. That is a pilot convenience, not a recommendation.

## Commands

Use these commands for the current v2.5.0 surface.

```bash
investorclaw ask "What's in my portfolio?"
investorclaw ask "How am I doing?"
investorclaw ask "Show my bond exposure"
investorclaw ask "Generate my end-of-day report"
investorclaw refresh               # Force fresh prices/news/cache
```

`investorclaw ask` eagerly runs the required backend commands, stores the signed JSON envelope, and narrates from authoritative output.

## Troubleshooting

Fix the issue that matches your setup.

### Cloud Authentication Errors

Run `hermes auth` to check credentials for the currently selected provider.

Switch providers if needed.

```bash
hermes model set --provider <p> --model <m>
```

### `ollama: command not found`

Install Ollama from https://ollama.ai.

### `Connection refused at localhost:11434`

Start Ollama with this command:

```bash
ollama serve
```

### Slow Local Responses

An 8B model typically runs at ~30-40 tok/s on CPU.

A GPU usually gives you a 2-3× speedup. That includes NVIDIA, AMD, and Apple Metal.

Switch to a smaller model, such as Mistral 7B, if RAM is the bottleneck.

### Model Not Found in Ollama

Pull the model first.

```bash
ollama pull <modelname>
```

Examples:

```bash
ollama pull hermes3:8b-q4_K_M
ollama pull mistral:latest
ollama pull qwen2.5-coder:7b
```

### Out of Memory

Use a smaller quantization or a smaller model. A 7B or 8B model uses less memory than a 70B model.

## vLLM for Speed

Use vLLM instead of Ollama if you want high-throughput local inference. Any HuggingFace-compatible model works.

```bash
python -m vllm.entrypoints.openai.api_server \
  --model NousResearch/Hermes-3-Llama-3.1-8B \
  --quantization bitsandbytes \
  --port 8000 &

hermes model set --provider openai-compat --endpoint http://localhost:8000/v1 --model NousResearch/Hermes-3-Llama-3.1-8B
```

## Learn More

- [Local Inference Setup](../docs/claw/shared/LOCAL_INFERENCE_GUIDE.md)
- [Architecture & Comparison](../docs/claw/shared/PLATFORM_COMPARISON.md)
- [Ollama Documentation](https://ollama.ai)
- [Hermes Model Card](https://huggingface.co/NousResearch/Hermes-3-Llama-3.1-8B)

## Next Steps

- Other Claw platforms? [Claw Home](../docs/claw/README.md)
- Claude Code? Use InvestorClaude; see [Claude Documentation](../docs/claude/README.md)
