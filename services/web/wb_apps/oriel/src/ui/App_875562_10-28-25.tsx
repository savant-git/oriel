import React, { useEffect, useState } from "react";
import "../theme/theme.css";

export default function App() {
  const [status, setStatus] = useState("Initializing oriel...");
  const [daemonActive, setDaemonActive] = useState(false);
  const [reportActive, setReportActive] = useState(false);

  useEffect(() => {
    // Check daemon status
    fetch("/api/daemon/status")
      .then(res => res.json())
      .then(data => {
        setDaemonActive(data.active || false);
        setStatus("✅ oriel main system running");
      })
      .catch(() => setStatus("⚠️ Could not connect to daemon"));
    
    // Check reports status
    fetch("/api/reports/status")
      .then(res => res.json())
      .then(data => {
        setReportActive(data.active || false);
      })
      .catch(() => setReportActive(false));
  }, []);

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>oriel</h1>
        <p>{status}</p>
      </header>
      <main className="app-main">
        <section className="module-panel">
          <h2>Core Modules</h2>
          <ul>
            <li>🧠 AI Engine</li>
            <li>🧩 Payload System</li>
            <li>📊 Data Visualization</li>
            <li>🎨 Branding Studio</li>
          </ul>
        </section>

        <section className="status-panel">
          <h2>Background Processes</h2>
          <div className="daemon-status">
            Daemon: {daemonActive ? "🟢 Running" : "🔴 Stopped"}
          </div>
          <div className="report-status">
            Reports: {reportActive ? "🟢 Running" : "🔴 Stopped"}
          </div>
        </section>
      </main>
      <footer className="app-footer">
        <p>oriel system online — intelligent creative engine</p>
      </footer>
    </div>
  );
}
