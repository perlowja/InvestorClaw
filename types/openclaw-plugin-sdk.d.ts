declare module "openclaw/plugin-sdk/plugin-entry" {
  export interface OpenClawToolDefinition {
    name: string;
    label?: string;
    description?: string;
    parameters?: unknown;
    execute?: (id: string, params: any) => unknown;
    [key: string]: unknown;
  }

  export interface OpenClawPluginApi {
    pluginConfig?: Record<string, string>;
    registerTool: (definition: OpenClawToolDefinition) => void;
    tool?: (definition: OpenClawToolDefinition) => void;
  }

  export interface OpenClawPluginDefinition {
    id?: string;
    name?: string;
    description?: string;
    kind?: string;
    reload?: unknown;
    nodeHostCommands?: unknown;
    securityAuditCollectors?: unknown;
    configSchema?: OpenClawPluginConfigSchema;
    register?: (api: OpenClawPluginApi) => void;
    [key: string]: unknown;
  }

  export type OpenClawPluginConfigSchema = Record<string, unknown>;

  export function definePluginEntry<T extends OpenClawPluginDefinition>(definition: T): T;
}
