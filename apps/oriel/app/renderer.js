// renderer.js
const logDiv = document.getElementById("log");
window.OrielAPI.onLog(text => {
  const span = document.createElement("div");
  span.textContent = text.trim();
  logDiv.appendChild(span);
  logDiv.scrollTop = logDiv.scrollHeight;
});
