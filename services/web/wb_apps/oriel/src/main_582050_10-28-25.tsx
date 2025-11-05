import React from "react";
import ReactDOM from "react-dom/client";
import App from "./ui/App";
import "./theme/theme.css";

// 🧠 oriel main entrypoint
ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <div
      style={{
        fontFamily: "Inter, sans-serif",
        backgroundColor: "#0f0f10",
        color: "#ffffff",
        height: "100vh",
        width: "100vw",
        overflow: "hidden",
      }}
    >
      <App />
    </div>
  </React.StrictMode>
);
