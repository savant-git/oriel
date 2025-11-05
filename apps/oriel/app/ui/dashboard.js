/**
 * dashboard.js
 * Phase 10 — Interactive Oriel Dashboard
 * Provides live kernel logs, control buttons, rate adjustment,
 * and opens the 3-D Resonance Space window.
 */

// Elements
const logEl = document.getElementById("log");
const canvas = document.getElementById("viz");
const ctx = canvas.getContext("2d");
const rateInput = document.getElementById("rate");
const pauseBtn = document.getElementById("pause");
const resumeBtn = document.getElementById("resume");

// simple scrolling bar graph of simulation activity
function draw(value) {
  ctx.fillStyle = "rgba(0,0,0,0.3)";
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = "#0f0";
  const h = (value % canvas.height);
  ctx.fillRect(canvas.width - 5, canvas.height - h, 4, h);
  ctx.translate(-5, 0);
  ctx.drawImage(canvas, 0, 0);
  ctx.setTransform(1, 0, 0, 1, 0, 0);
}

// listen for kernel output
window.OrielAPI.onLog((text) => {
  logEl.textContent += text;
  logEl.scrollTop = logEl.scrollHeight;

  // extract numeric payloads for visualization
  try {
    const match = text.match(/Payloads:\s*(\d+)/);
    if (match) {
      const val = parseInt(match[1]);
      draw(val);
    }
  } catch {
    /* ignore parse errors */
  }
});

// Control buttons
pauseBtn.onclick = () => window.OrielAPI.sendCommand("pause");
resumeBtn.onclick = () => window.OrielAPI.sendCommand("resume");
rateInput.onchange = (e) =>
  window.OrielAPI.sendCommand("rate", parseInt(e.target.value));

// Create and attach "Open Resonance Space" button dynamically
const openBtn = document.createElement("button");
openBtn.textContent = "Open Resonance Space";
openBtn.id = "openResonance";
document.getElementById("controls").appendChild(openBtn);
openBtn.onclick = () => window.OrielAPI.openResonance();

// Minor UI feedback
function flashButton(btn) {
  const old = btn.style.backgroundColor;
  btn.style.backgroundColor = "#3f3";
  setTimeout(() => (btn.style.backgroundColor = old || "#222"), 150);
}

pauseBtn.addEventListener("click", () => flashButton(pauseBtn));
resumeBtn.addEventListener("click", () => flashButton(resumeBtn));
openBtn.addEventListener("click", () => flashButton(openBtn));

// handle window resize for canvas
window.addEventListener("resize", () => {
  canvas.width = window.innerWidth - 50;
  canvas.height = 500;
});
canvas.width = window.innerWidth - 50;
canvas.height = 500;
