#!/usr/bin/env node
import fs from "fs";
import path from "path";
const root = path.resolve("./src");
const map = {};
function walk(dir) {
  for (const f of fs.readdirSync(dir)) {
    const full = path.join(dir, f);
    if (fs.statSync(full).isDirectory()) walk(full);
    else if (/\.(ts|tsx|js|jsx|css)$/.test(f)) {
      const content = fs.readFileSync(full, "utf8");
      const imports = [...content.matchAll(/from ["'](.*?)["']/g)].map(m=>m[1]);
      map[full] = { imports };
    }
  }
}
walk(root);
fs.writeFileSync("context-map.yaml",
  Object.entries(map).map(([f,d])=>`${f}:\n  imports:\n${d.imports.map(i=>`    - ${i}`).join("\n")}`).join("\n"));
console.log("✅ Context map updated.");
