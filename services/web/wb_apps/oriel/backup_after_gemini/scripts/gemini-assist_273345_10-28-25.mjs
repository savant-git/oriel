#!/usr/bin/env node
/**
 * Gemini Assist – Context-Aware File Optimizer for oriel
 * Enforces strict source-code output (no Markdown or commentary).
 */
import fs from "fs";
import fetch from "node-fetch";
import path from "path";

const API_KEY = process.env.GEMINI_API_KEY;
if (!API_KEY) {
  console.error("❌ No GEMINI_API_KEY found. Run: export GEMINI_API_KEY='YOUR_KEY'");
  process.exit(1);
}

const MODEL = "models/gemini-2.5-pro-latest";
const ENDPOINT = `https://generativelanguage.googleapis.com/v1beta/models/${MODEL}:generateContent?key=${API_KEY}`;

const [,, cmd, file, ...promptParts] = process.argv;
const prompt = promptParts.join(" ");
if (!cmd || !file || !prompt) {
  console.error("Usage: node scripts/gemini-assist.mjs edit <file> \"Prompt text\"");
  process.exit(1);
}

async function run() {
  console.log(`🧠 Editing file: ${file}`);
  console.log(`📝 Prompt: ${prompt}`);

  const ext = path.extname(file).toLowerCase();
  const lang = ext === ".ts" || ext === ".tsx" ? "TypeScript"
             : ext === ".js" || ext === ".jsx" ? "JavaScript"
             : ext === ".css" ? "CSS"
             : ext === ".json" ? "JSON"
             : "Text";

  const content = fs.existsSync(file) ? fs.readFileSync(file, "utf8") : "";

  // Strict context to stop Gemini from adding ``` wrappers or commentary
  const body = {
    contents: [
      {
        role: "user",
        parts: [{
          text:
`You are optimizing a live oriel application source file.
The file is written in ${lang}. You must:
- Output ONLY valid ${lang} code — NO markdown, NO backticks, NO commentary.
- Preserve file structure and imports exactly unless optimization demands change.
- Do not prepend documentation, comments, or explanations.
- Never wrap output in triple backticks.
- If optimization cannot be applied safely, return the unmodified source.
- Ensure syntax validity and maintain TypeScript/JSX semantics.
Existing File Content:
${content}

Instruction:
${prompt}`
        }]
      }
    ],
    generationConfig: {
      temperature: 0.8,
      topK: 40,
      topP: 0.9,
      maxOutputTokens: 8192,
    },
  };

  const res = await fetch(ENDPOINT, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  const data = await res.json();
  const output = data?.candidates?.[0]?.content?.parts?.[0]?.text;

  if (!output) {
    console.error("⚠️ Gemini returned no valid code.\nFull response:", JSON.stringify(data, null, 2));
    process.exit(1);
  }

  // Sanitize residual ``` or Markdown fences just in case
  const cleanOutput = output
    .replace(/^```[a-zA-Z]*\s*/gm, "")
    .replace(/```$/gm, "")
    .replace(/^"typescript/gm, "")
    .trim();

  fs.writeFileSync(file, cleanOutput, "utf8");
  console.log(`✅ File optimized successfully: ${file}`);
}

run().catch(err => {
  console.error("💥 Gemini Assist failed:", err);
  process.exit(1);
});
