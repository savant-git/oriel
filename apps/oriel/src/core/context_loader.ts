/**
 * context_loader.ts
 * Loads payloads and directives for runtime context.
 */

import fs from "fs";
import path from "path";

export interface OrielContext {
  directives: Record<string, any>;
  payloads: Record<string, any>;
}

export async function loadContext(): Promise<OrielContext> {
  const base = path.resolve(process.cwd(), "payloads");
  const directivesPath = path.resolve(process.cwd(), "docs/oriel_directive.json");

  const directives = JSON.parse(fs.readFileSync(directivesPath, "utf-8"));
  const payloadFiles = fs.readdirSync(base).filter(f => f.endsWith(".json"));

  const payloads: Record<string, any> = {};
  for (const file of payloadFiles) {
    const key = file.replace(".json", "");
    const data = JSON.parse(fs.readFileSync(path.join(base, file), "utf-8"));
    payloads[key] = data;
  }

  return { directives, payloads };
}
