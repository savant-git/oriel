#!/usr/bin/env node
import fs from "fs";

const logFile = "logs/iteration.log";
const outFile = "reports/summary.html";
if (!fs.existsSync(logFile)) process.exit(0);

const content = fs.readFileSync(logFile, "utf8")
  .split("\n")
  .filter(Boolean)
  .slice(-300)
  .join("\n");

const html = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<title>oriel Iteration Summary</title>
<style>
body { font-family: Inter, sans-serif; background: #111; color: #eee; padding: 2rem; }
h1 { color: #6fb3ff; }
pre { background: #222; padding: 1rem; border-radius: 8px; overflow-x: auto; }
footer { color: #777; margin-top: 2rem; font-size: 0.9rem; }
</style>
</head>
<body>
<h1>🧠 oriel Iteration Summary</h1>
<pre>${content}</pre>
<footer>Generated ${new Date().toLocaleString()}</footer>
</body>
</html>`;
fs.writeFileSync(outFile, html);
console.log("📊 Summary report generated →", outFile);
