# Disclaimer

InvestorClaw is financial software intended for portfolio analysis, market data
review, and narrative exploration. Use it with care and independently verify
all outputs before relying on them.

## Educational Use Only

InvestorClaw is provided for educational and informational use only. It is not
investment, legal, tax, accounting, or financial planning advice. The project,
maintainers, contributors, software outputs, model responses, examples, and
documentation do not create a fiduciary duty or advisory relationship with any
user.

You are solely responsible for investment decisions, trading decisions,
portfolio construction, risk management, compliance obligations, and any losses
or consequences resulting from use of this software.

## No Warranty

InvestorClaw is provided "as is" and "as available" without warranties of any
kind, express or implied, including but not limited to warranties of accuracy,
availability, completeness, merchantability, fitness for a particular purpose,
title, and non-infringement.

Market data, economic data, provider responses, generated narratives, and
derived calculations may be delayed, incomplete, stale, incorrect, or
unavailable. Do not treat any output as authoritative.

## Provider Data Flows

Depending on configuration, InvestorClaw may send prompts, queries, portfolio
context, ticker symbols, or other user-provided inputs to third-party or local
providers. Review each provider's terms and privacy practices before enabling
the corresponding integration.

Provider data flows include:

* Together AI: default LLM narrative.
* Google AI Studio: optional consult.
* local llama.cpp: optional consult.
* NewsAPI: market news when key configured.
* Finnhub: market data when key configured.
* Alpha Vantage: market data when key configured.
* FRED: economic data when key configured.
* Polygon-via-Massive: market data when key configured.
