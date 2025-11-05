#!/usr/bin/env node
/**
 * 🧠 oriel Live Dashboard Server
 * Displays daemon & optimization status in real-time.
 */
import express from "express";
import fs from "fs";
import os from "os";
import chokidar from "chokidar";

const app = express();
const PORT = process.env.PORT || 5175;
const LOG_FILE = "logs/daemon_enhanced.log";
const STATUS_FILE = "logs/daemon_status.json";

function getCPUload() {
  const load = os.loadavg()[0] * 100;
  return load.toFixed(1);
}

function getLastLines(file, n = 20) {
  if (!fs.existsSync(file)) return [];
  const lines = fs.readFileSync(file, "utf8").trim().split("\n");
  return lines.slice(-n);
}

app.get("/api/status", (req, res) => {
  const data = fs.existsSync(STATUS_FILE)
    ? JSON.parse(fs.readFileSync(STATUS_FILE, "utf8"))
    : { running: false, lastCycle: "N/A" };
  res.json({
    ...data,
    cpu: getCPUload(),
    uptime: os.uptime(),
    recent: getLastLines(LOG_FILE, 10),
  });
});

app.use(express.static("public"));
app.listen(PORT, () =>
  console.log(`📊 oriel Dashboard running → http://localhost:${PORT}/dashboard`)
);

// Write daemon activity heartbeat
setInterval(() => {
  const status = {
    running: true,
    timestamp: new Date().toISOString(),
    uptime: os.uptime(),
  };
  fs.writeFileSync(STATUS_FILE, JSON.stringify(status, null, 2));
}, 15000);
