/**
 * InvestorClaw — OpenClaw native plugin entry point.
 *
 * Wraps the Python-based investorclaw.py CLI as a set of typed agent tools.
 * Each tool spawns `python3 investorclaw.py <command>` in a subprocess with
 * API-key env vars forwarded from the plugin config.
 */

import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
import { Type } from "@sinclair/typebox";
import { execFile } from "node:child_process";
import { promisify } from "node:util";
import * as path from "node:path";
import * as os from "node:os";
import { fileURLToPath } from "node:url";

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

    // Resolve the directory containing this file (skill/) to locate investorclaw.py.
    const selfDir =
      api.rootDir ??
      path.dirname(fileURLToPath(import.meta.url));
    const entryScript = path.join(selfDir, "investorclaw.py");

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

      // CRITICAL: Set PYTHONPATH so that 'from lib.xxx import ...' resolves correctly.
      // selfDir is the skill root (investorclaw/); lib/ is directly inside it.
      // Also include parent dir for any top-level package imports.
      const investorClawDir = path.dirname(selfDir);  // parent of skill root
      const skillDir = selfDir;  // skill root (investorclaw/)
      const pythonpath = `${investorClawDir}:${skillDir}`;
      if (env.PYTHONPATH) {
        env.PYTHONPATH = `${pythonpath}:${env.PYTHONPATH}`;
      } else {
        env.PYTHONPATH = pythonpath;
      }

      return env;
    }

    /**
     * Spawn `python3 investorclaw.py <command> [...args]` and return stdout.
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
        console.log(`[InvestorClaw] Running: python3 ${entryScript} ${command}`);
        console.log(`[InvestorClaw] selfDir: ${selfDir}`);
        console.log(`[InvestorClaw] entryScript: ${entryScript}`);
        console.log(`[InvestorClaw] PYTHONPATH: ${env.PYTHONPATH}`);
        console.log(`[InvestorClaw] cwd: ${selfDir}`);

        const { stdout, stderr } = await execFileAsync(
          "python3",
          [entryScript, command, ...args],
          { env, cwd: selfDir, timeout: timeoutMs },
        );
        return (stdout || stderr).trim();
      } catch (err: unknown) {
        const e = err as { stdout?: string; stderr?: string; message?: string };
        return (e.stdout || e.stderr || e.message || String(err)).trim();
      }
    }

    // ------------------------------------------------------------------
    // Tools
    // ------------------------------------------------------------------

    api.registerTool({
      name: "investorclaw_setup",
      description:
        "Run initial portfolio setup. Discovers PDF, Excel, and CSV files in the " +
        "portfolios/ directory, extracts tables, and consolidates them into " +
        "master_portfolio.csv. Run this once before other tools.",
      parameters: Type.Object({}),
      async execute(_id, _p) {
        return { content: [{ type: "text", text: await run("setup", [], QUICK_TIMEOUT_MS) }] };
      },
    });

    api.registerTool({
      name: "investorclaw_holdings",
      description:
        "Get a portfolio snapshot with current prices for every holding in " +
        "master_portfolio.csv. Fetches live quotes via Finnhub → Polygon → " +
        "Alpha Vantage → yfinance (first available). Returns JSON saved to " +
        "portfolio_reports/holdings.json.",
      parameters: Type.Object({}),
      async execute(_id, _p) {
        return { content: [{ type: "text", text: await run("holdings") }] };
      },
    });

    api.registerTool({
      name: "investorclaw_performance",
      description:
        "Analyze portfolio performance: YTD and 12-month returns, Sharpe ratio, " +
        "beta, volatility, max drawdown. Requires holdings.json from " +
        "investorclaw_holdings. Returns JSON saved to portfolio_reports/performance.json.",
      parameters: Type.Object({}),
      async execute(_id, _p) {
        return { content: [{ type: "text", text: await run("performance") }] };
      },
    });

    api.registerTool({
      name: "investorclaw_analysis",
      description:
        "Run a full portfolio analysis combining the holdings snapshot with " +
        "performance metrics. Requires holdings.json from investorclaw_holdings. " +
        "Returns JSON saved to portfolio_reports/portfolio_analysis.json.",
      parameters: Type.Object({}),
      async execute(_id, _p) {
        return { content: [{ type: "text", text: await run("analysis") }] };
      },
    });

    api.registerTool({
      name: "investorclaw_bonds",
      description:
        "Analyze fixed-income holdings: exact YTM, modified duration, convexity, " +
        "tax-equivalent yield for munis, and benchmark spread vs. FRED live " +
        "Treasury/TIPS yield curve (falls back to April 2026 seeds if FRED_API_KEY " +
        "is absent). Returns JSON saved to portfolio_reports/bond_analysis.json.",
      parameters: Type.Object({}),
      async execute(_id, _p) {
        return { content: [{ type: "text", text: await run("bonds") }] };
      },
    });

    api.registerTool({
      name: "investorclaw_fixed_income",
      description:
        "Generate a fixed-income strategy report with yield curve positioning, " +
        "duration risk, and rebalancing recommendations. Returns JSON saved to " +
        "portfolio_reports/fixed_income_analysis.json.",
      parameters: Type.Object({}),
      async execute(_id, _p) {
        return { content: [{ type: "text", text: await run("fixed-income") }] };
      },
    });

    api.registerTool({
      name: "investorclaw_news",
      description:
        "Fetch and summarize recent news correlated to portfolio holdings. " +
        "Requires NEWSAPI_KEY and holdings.json from investorclaw_holdings. " +
        "Returns JSON saved to portfolio_reports/portfolio_news.json.",
      parameters: Type.Object({}),
      async execute(_id, _p) {
        return { content: [{ type: "text", text: await run("news") }] };
      },
    });

    api.registerTool({
      name: "investorclaw_analyst",
      description:
        "Get analyst consensus ratings and price targets for portfolio holdings. " +
        "Uses Finnhub and/or Polygon. Requires holdings.json from " +
        "investorclaw_holdings. Returns JSON saved to portfolio_reports/analyst_data.json.",
      parameters: Type.Object({}),
      async execute(_id, _p) {
        return { content: [{ type: "text", text: await run("analyst") }] };
      },
    });

    api.registerTool({
      name: "investorclaw_report",
      description:
        "Export portfolio data to CSV or Excel. Requires holdings.json from " +
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
        return { content: [{ type: "text", text: await run(cmd) }] };
      },
    });

    api.registerTool({
      name: "investorclaw_session",
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
        return { content: [{ type: "text", text: await run("session", args, QUICK_TIMEOUT_MS) }] };
      },
    });

    api.registerTool({
      name: "investorclaw_lookup",
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
        return { content: [{ type: "text", text: await run("lookup", args, QUICK_TIMEOUT_MS) }] };
      },
    });

    api.registerTool({
      name: "investorclaw_ollama_setup",
      description:
        "Check Ollama endpoint availability and list models suitable for " +
        "InvestorClaw consultation (tier-3 enrichment). Use this to verify the " +
        "local LLM setup before enabling INVESTORCLAW_CONSULTATION_ENABLED.",
      parameters: Type.Object({}),
      async execute(_id, _p) {
        return {
          content: [{ type: "text", text: await run("ollama-setup", [], QUICK_TIMEOUT_MS) }],
        };
      },
    });

    api.registerTool({
      name: "investorclaw_guardrails",
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
        return {
          content: [{ type: "text", text: await run("guardrails", args, QUICK_TIMEOUT_MS) }],
        };
      },
    });
  },
});
