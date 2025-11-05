#!/usr/bin/env node
import fs from "fs";
import { execSync } from "child_process";

const cfg = JSON.parse(fs.readFileSync("scripts/oriel.config.json", "utf8"));
const target = process.argv[2] || "";
if (!target) { console.error("Usage: node scripts/iterate_oriel.mjs <description>"); process.exit(1); }

function log(msg){ fs.appendFileSync(cfg.logFile, `[${new Date().toISOString()}] ${msg}\n`); }

console.log("🔁 Starting 10× iteration pipeline...");
for (let i=1;i<=cfg.iterations;i++){
  console.log(`🌀 Iteration ${i}/10`);
  try{
    execSync("bash scripts/self_heal.sh",{stdio:"ignore"});
    execSync("node scripts/context_map.mjs",{stdio:"ignore"});
    log(`Iteration ${i} complete: ${target}`);
  }catch(e){ log(`Iteration ${i} failed: ${e.message}`); }
}
console.log("✅ Iteration cycle complete.");
