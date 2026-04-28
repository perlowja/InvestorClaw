// Copyright 2026 InvestorClaw Contributors
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.


/**
 * InvestorClaw — OpenClaw native plugin entry point.
 *
 * Wraps the Python-based investorclaw.py CLI as a set of typed agent tools.
 * Each tool spawns the `investorclaw` venv binary in a subprocess with
 * API-key env vars forwarded from the plugin config. The venv binary is
 * the canonical cross-environment entry post-Phase-2 (v2.3.0); pre-v2.3.0
 * builds invoked `python3 investorclaw.py <command>` against a raw system
 * Python which is no longer guaranteed to have ic-engine importable.
 */

import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
import { Type } from "@sinclair/typebox";
import { execFile } from "node:child_process";
import * as fs from "node:fs";
import * as path from "node:path";
import { promisify } from "node:util";

const execFileAsync = promisify(execFile);

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const ENV_KEYS = [
  "FINNHUB_KEY",
  "NEWSAPI_KEY",
  "MASSIVE_API_KEY",
  "ALPHA_VANTAGE_KEY",
  "FRED_API_KEY",
  "INVESTOR_CLAW_REPORTS_DIR",
  "INVESTOR_CLAW_PORTFOLIO_DIR",
  "INVESTORCLAW_CONSULTATION_ENABLED",
  "INVESTORCLAW_CONSULTATION_ENDPOINT",
  "INVESTORCLAW_CONSULTATION_MODEL",
  "INVESTORCLAW_CONSULTATION_HMAC_KEY",
  "INVESTORCLAW_CARD_FORMAT",
  "INVESTORCLAW_STONKMODE_PROVIDER",
  "INVESTORCLAW_STONKMODE_ENDPOINT",
  "INVESTORCLAW_STONKMODE_API_KEY",
  "INVESTORCLAW_STONKMODE_MODEL",
] as const;

// Generous timeout for analysis commands that hit external APIs (ms).
const ANALYSIS_TIMEOUT_MS = 120_000;
// Faster timeout for read-only / local commands.
const QUICK_TIMEOUT_MS = 30_000;

// ---------------------------------------------------------------------------
// Plugin entry
// ---------------------------------------------------------------------------

export default definePluginEntry({
  id: "investorclaw",
  name: "InvestorClaw",
  description:
    "Portfolio analysis: holdings snapshots, performance metrics, bond analytics " +
    "(YTM, duration, FRED yield curve), analyst ratings, news correlation, and " +
    "CSV/Excel exports. Educational guardrails enforced on all outputs.",

  register(api) {
    const pluginConfig = (api.pluginConfig ?? {}) as Record<string, string>;

    // Resolve the skill directory: prefer INVESTORCLAW_SKILL_ROOT env/config,
    // then derive from this file's own location (works whether installed as a
    // linked plugin from the canonical repo or copied into extensions/).
    const skillRoot =
      pluginConfig["INVESTORCLAW_SKILL_ROOT"] ??
      process.env.INVESTORCLAW_SKILL_ROOT ??
      path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");

    // Phase 2 of IC_DECOMPOSITION (InvestorClaw v2.3.0): the engine moved to
    // ic-engine and the InvestorClaw shim is no longer guaranteed importable
    // by raw `python3`. Resolve a binary path that works across installer
    // layouts AND non-shell-launched OpenClaw apps where ~/.local/bin may
    // not be on PATH:
    //
    //   1. INVESTORCLAW_CLI env override.
    //   2. openclaw/install.sh path: ~/.cache/investorclaw/.venv/bin/investorclaw
    //   3. standalone/install.sh path: ${skillRoot}/.venv/bin/investorclaw
    //   4. The user-facing symlink: ~/.local/bin/investorclaw
    //   5. Bare 'investorclaw' (PATH-resolved fallback for shell launches).
    function resolveCliBinary(): string {
      if (process.env.INVESTORCLAW_CLI) return process.env.INVESTORCLAW_CLI;
      const home = process.env.HOME ?? "";
      // Order matters: prefer the venv physically under skillRoot first so
      // a dev checkout with its own .venv beats a stale global cache. Then
      // openclaw/install.sh's standard cache path. Then the user-PATH symlink.
      const candidates = [
        path.join(skillRoot, ".venv", "bin", "investorclaw"),
        path.join(home, ".cache", "investorclaw", ".venv", "bin", "investorclaw"),
        path.join(home, ".local", "bin", "investorclaw"),
      ];
      for (const c of candidates) {
        try { if (fs.existsSync(c)) return c; } catch { /* skip */ }
      }
      return "investorclaw";
    }
    const cliBinary = resolveCliBinary();

    // ------------------------------------------------------------------
    // Helpers
    // ------------------------------------------------------------------

    /** Build a process env with plugin config keys forwarded. */
    function buildEnv(): NodeJS.ProcessEnv {
      const env: NodeJS.ProcessEnv = { ...process.env };
      for (const key of ENV_KEYS) {
        const val = pluginConfig[key];
        if (val) env[key] = val;
      }

      // Phase 2: hand the resolved skill root to the InvestorClaw shim
      // explicitly so it doesn't have to probe well-known checkout paths.
      // ic-engine v2.4.1+ honors this in cli.py's SKILL_DIR resolution.
      env.INVESTORCLAW_SKILL_DIR = skillRoot;

      // PYTHONPATH: keep parent + skillRoot prepended for any subprocess
      // that still imports adapter-side helpers from there. ic-engine itself
      // lives in the venv's site-packages and doesn't need this.
      const investorClawDir = path.dirname(skillRoot);
      const pythonpath = `${investorClawDir}:${skillRoot}`;
      if (env.PYTHONPATH) {
        env.PYTHONPATH = `${pythonpath}:${env.PYTHONPATH}`;
      } else {
        env.PYTHONPATH = pythonpath;
      }

      return env;
    }

    /**
     * Spawn the `investorclaw` venv binary `<command> [...args]` and return
     * stdout. The binary, installed by `uv sync` in openclaw/install.sh,
     * routes through the InvestorClaw shim which sets INVESTORCLAW_SKILL_DIR
     * + loads the skill-checkout's .env before delegating to ic_engine.cli.
     *
     * Pre-Phase-2 builds shipped this as `python3 investorclaw.py <command>`,
     * which relied on a raw system Python with ic-engine pre-installed.
     * That assumption no longer holds; the venv binary is the canonical
     * cross-environment entrypoint.
     *
     * On non-zero exit the stderr is captured and returned as content so the
     * agent can surface the error message rather than throwing.
     */
    async function run(
      command: string,
      args: string[] = [],
      timeoutMs = ANALYSIS_TIMEOUT_MS,
    ): Promise<string> {
      try {
        const env = buildEnv();
        console.log(`[InvestorClaw] Running: ${cliBinary} ${command}`);
        console.log(`[InvestorClaw] skillRoot: ${skillRoot}`);
        console.log(`[InvestorClaw] cliBinary: ${cliBinary}`);
        console.log(`[InvestorClaw] PYTHONPATH: ${env.PYTHONPATH}`);
        console.log(`[InvestorClaw] cwd: ${skillRoot}`);

        const { stdout, stderr } = await execFileAsync(
          cliBinary,
          [command, ...args],
          { env, cwd: skillRoot, timeout: timeoutMs },
        );
        return (stdout || stderr).trim();
      } catch (err: unknown) {
        const e = err as { stdout?: string; stderr?: string; message?: string };
        const partial = (e.stdout || "").trim();
        const errMsg  = (e.stderr || e.message || String(err)).trim();
        // When the subprocess produced partial stdout before crashing, wrap it so
        // the agent still sees the disclaimer even on error paths.
        if (partial) {
          return JSON.stringify({
            disclaimer: "⚠️  EDUCATIONAL ANALYSIS - NOT INVESTMENT ADVICE",
            is_investment_advice: false,
            error: "subprocess_error",
            partial_output: partial,
            stderr: errMsg || undefined,
          });
        }
        return errMsg;
      }
    }

    // ------------------------------------------------------------------
    // Helpers
    // ------------------------------------------------------------------

    /** Wrap a text string as an AgentToolResult (content + required details). */
    function tr(text: string) {
      return { content: [{ type: "text" as const, text }], details: {} };
    }

    // ------------------------------------------------------------------
    // Tools
    // ------------------------------------------------------------------

    api.registerTool({
      name: "investorclaw_setup",
      label: "Setup Portfolio",
      description:
        "Run initial portfolio setup. Discovers PDF, Excel, and CSV files in the " +
        "portfolios/ directory, extracts tables, and consolidates them into " +
        "master_portfolio.csv. Run this once before other tools.",
      parameters: Type.Object({}),
      async execute(_id, _p) {
        return tr(await run("setup", [], QUICK_TIMEOUT_MS));
      },
    });

    api.registerTool({
      name: "investorclaw_holdings",
      label: "Portfolio Holdings",
      description:
        "Get a portfolio snapshot with current prices for every holding in " +
        "master_portfolio.csv. Fetches live quotes via Finnhub → Massive → " +
        "Alpha Vantage → yfinance (first available). Emits compact JSON and " +
        "saves portfolio_reports/holdings_summary.json plus full data in .raw/holdings.json.",
      parameters: Type.Object({}),
      async execute(_id, _p) {
        return tr(await run("holdings"));
      },
    });

    api.registerTool({
      name: "investorclaw_performance",
      label: "Portfolio Performance",
      description:
        "Analyze portfolio performance: YTD and 12-month returns, Sharpe ratio, " +
        "beta, volatility, max drawdown. Requires the holdings snapshot from " +
        "investorclaw_holdings. Returns JSON saved to portfolio_reports/performance.json.",
      parameters: Type.Object({}),
      async execute(_id, _p) {
        return tr(await run("performance"));
      },
    });

    api.registerTool({
      name: "investorclaw_analysis",
      label: "Portfolio Analysis",
      description:
        "Run a full portfolio analysis combining the holdings snapshot with " +
        "performance metrics. Requires investorclaw_holdings first. " +
        "Returns JSON saved to portfolio_reports/portfolio_analysis.json.",
      parameters: Type.Object({}),
      async execute(_id, _p) {
        return tr(await run("analysis"));
      },
    });

    api.registerTool({
      name: "investorclaw_bonds",
      label: "Bond Analysis",
      description:
        "Analyze fixed-income holdings: exact YTM, modified duration, convexity, " +
        "tax-equivalent yield for munis, and benchmark spread vs. FRED live " +
        "Treasury/TIPS yield curve (falls back to April 2026 seeds if FRED_API_KEY " +
        "is absent). Returns JSON saved to portfolio_reports/bond_analysis.json.",
      parameters: Type.Object({}),
      async execute(_id, _p) {
        return tr(await run("bonds"));
      },
    });

    api.registerTool({
      name: "investorclaw_fixed_income",
      label: "Fixed Income Report",
      description:
        "Generate a fixed-income strategy report with yield curve positioning, " +
        "duration risk, and rebalancing recommendations. Returns JSON saved to " +
        "portfolio_reports/fixed_income_analysis.json.",
      parameters: Type.Object({}),
      async execute(_id, _p) {
        return tr(await run("fixed-income"));
      },
    });

    api.registerTool({
      name: "investorclaw_news",
      label: "Portfolio News",
      description:
        "Fetch and summarize recent news correlated to portfolio holdings. " +
        "Requires NEWSAPI_KEY and investorclaw_holdings first. " +
        "Returns JSON saved to portfolio_reports/portfolio_news.json.",
      parameters: Type.Object({}),
      async execute(_id, _p) {
        return tr(await run("news"));
      },
    });

    api.registerTool({
      name: "investorclaw_analyst",
      label: "Analyst Ratings",
      description:
        "Get analyst consensus ratings and price targets for portfolio holdings. " +
        "Uses Finnhub and/or Massive. Requires the holdings snapshot from " +
        "investorclaw_holdings. Returns JSON saved to portfolio_reports/analyst_data.json.",
      parameters: Type.Object({}),
      async execute(_id, _p) {
        return tr(await run("analyst"));
      },
    });

    api.registerTool({
      name: "investorclaw_report",
      label: "Export Report",
      description:
        "Export portfolio data to CSV or Excel. Requires the holdings snapshot from " +
        "investorclaw_holdings. Returns the path of the generated report file.",
      parameters: Type.Object({
        format: Type.Optional(
          Type.Union(
            [Type.Literal("csv"), Type.Literal("excel")],
            { description: "Export format. Defaults to csv." },
          ),
        ),
      }),
      async execute(_id, params) {
        const cmd = params.format === "excel" ? "excel" : "csv";
        return tr(await run(cmd));
      },
    });

    api.registerTool({
      name: "investorclaw_session",
      label: "Risk Session",
      description:
        "Initialize a risk-calibration session before running analysis. Sets a " +
        "heat level (1 = very conservative … 10 = aggressive) and optional macro " +
        "concerns that bias the guardrail messaging for the session.",
      parameters: Type.Object({
        heat_level: Type.Optional(
          Type.Integer({
            minimum: 1,
            maximum: 10,
            description: "Risk tolerance: 1 = very conservative, 10 = aggressive.",
          }),
        ),
        concerns: Type.Optional(
          Type.String({
            description:
              "Comma-separated macro concerns, e.g. 'inflation,rates,recession'.",
          }),
        ),
      }),
      async execute(_id, params) {
        const args: string[] = [];
        if (params.heat_level != null) args.push("--heat-level", String(params.heat_level));
        if (params.concerns) args.push("--concerns", params.concerns);
        return tr(await run("session", args, QUICK_TIMEOUT_MS));
      },
    });

    api.registerTool({
      name: "investorclaw_lookup",
      label: "Symbol Lookup",
      description:
        "Look up detailed data for a specific ticker symbol from cached .raw/ files " +
        "(holdings, analyst, or news data). Faster than re-running a full command " +
        "when only one symbol is needed.",
      parameters: Type.Object({
        symbol: Type.String({ description: "Ticker symbol, e.g. MSFT" }),
        file: Type.Optional(
          Type.Union(
            [
              Type.Literal("holdings"),
              Type.Literal("analyst"),
              Type.Literal("news"),
            ],
            { description: "Which dataset to query. Defaults to holdings." },
          ),
        ),
      }),
      async execute(_id, params) {
        const args = ["--symbol", params.symbol.toUpperCase()];
        if (params.file) args.push("--file", params.file);
        return tr(await run("lookup", args, QUICK_TIMEOUT_MS));
      },
    });

    api.registerTool({
      name: "investorclaw_ollama_setup",
      label: "Ollama Setup",
      description:
        "Check Ollama endpoint availability and list models suitable for " +
        "InvestorClaw consultation (tier-3 enrichment). Use this to verify the " +
        "local LLM setup before enabling INVESTORCLAW_CONSULTATION_ENABLED.",
      parameters: Type.Object({}),
      async execute(_id, _p) {
        return tr(await run("ollama-setup", [], QUICK_TIMEOUT_MS));
      },
    });

    api.registerTool({
      name: "investorclaw_guardrails",
      label: "Guardrails",
      description:
        "Inspect or interact with InvestorClaw's financial-advice guardrails. " +
        "'status' reports current enforcement state. 'prime' injects the " +
        "educational disclaimer preamble into the session. 'query' runs a " +
        "financial question through per-turn guardrail injection.",
      parameters: Type.Object({
        action: Type.Optional(
          Type.Union(
            [Type.Literal("status"), Type.Literal("prime")],
            {
              description:
                "'status' — show enforcement state. " +
                "'prime' — inject calibration preamble. " +
                "Omit to run a plain guardrail check.",
            },
          ),
        ),
        query: Type.Optional(
          Type.String({
            description:
              "Financial question to run through per-turn guardrail injection.",
          }),
        ),
      }),
      async execute(_id, params) {
        const args: string[] = [];
        if (params.action === "prime") args.push("--prime");
        if (params.query) args.push("--query", params.query);
        return tr(await run("guardrails", args, QUICK_TIMEOUT_MS));
      },
    });

    api.registerTool({
      name: "investorclaw_update_identity",
      label: "Update Identity",
      description:
        "Inject InvestorClaw data-integrity and financial-advice guardrail rules into the " +
        "workspace IDENTITY.md file. Run this once per session before any analysis commands " +
        "to ensure the agent enforces file-authority rules and educational-framing guardrails. " +
        "Required before W1 in harness runs. Emits ic_result envelope on completion.",
      parameters: Type.Object({}),
      async execute(_id, _p) {
        return tr(await run("update-identity", [], QUICK_TIMEOUT_MS));
      },
    });

    api.registerTool({
      name: "investorclaw_stonkmode",
      label: "Stonkmode",
      description:
        "Control the Stonkmode entertainment narration layer. " +
        "'on' activates stonkmode and randomly selects a lead+foil pair from 26 " +
        "fictional finance personalities across 8 archetypes. Use --lead and --foil " +
        "to force a specific pair (persona IDs, e.g. chico_reyes / farout_farley). " +
        "'off' deactivates and removes state. 'status' shows active pair and segment count. " +
        "Once active, every /portfolio analysis command emits a stonkmode_narration " +
        "JSON block with satirical in-character commentary. consultation_mode is always " +
        "'deactivated' in stonkmode output — it is entertainment, not advice.",
      parameters: Type.Object({
        action: Type.Optional(
          Type.Union(
            [
              Type.Literal("on"),
              Type.Literal("off"),
              Type.Literal("status"),
            ],
            {
              description:
                "'on' — activate stonkmode (random or forced pair). " +
                "'off' — deactivate and clear state. " +
                "'status' — show active pair. Omit to show status.",
            },
          ),
        ),
        lead: Type.Optional(
          Type.String({
            description:
              "Force a specific lead persona by ID (e.g. 'blitz_thunderbuy'). " +
              "Requires action='on'.",
          }),
        ),
        foil: Type.Optional(
          Type.String({
            description:
              "Force a specific foil persona by ID (e.g. 'victor_voss'). " +
              "Requires action='on'.",
          }),
        ),
      }),
      async execute(_id, params) {
        const args: string[] = [];
        if (params.action) args.push(params.action);
        if (params.lead) { args.push("--lead"); args.push(params.lead); }
        if (params.foil) { args.push("--foil"); args.push(params.foil); }
        return tr(await run("stonkmode", args, QUICK_TIMEOUT_MS));
      },
    });
  },
});
