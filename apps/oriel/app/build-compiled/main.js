/**
 * main.ts — Oriel Desktop main process with auto-update
 */
import { app, BrowserWindow, dialog } from "electron";
import { autoUpdater } from "electron-updater";
import path from "path";
let mainWindow = null;
function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        webPreferences: {
            preload: path.join(__dirname, "preload.js"),
            contextIsolation: true,
            nodeIntegration: false
        },
        icon: path.join(__dirname, "../build/icons/512x512.png"),
        title: "Oriel"
    });
    mainWindow.loadFile("index.html");
    mainWindow.on("closed", () => (mainWindow = null));
    // Optional: show devtools when running in dev mode
    if (!app.isPackaged)
        mainWindow.webContents.openDevTools();
}
// ----------------------
// Auto-update handlers
// ----------------------
autoUpdater.autoDownload = true;
autoUpdater.on("checking-for-update", () => {
    sendStatus("Checking for updates…");
});
autoUpdater.on("update-available", info => {
    sendStatus(`Update available: ${info.version}. Downloading…`);
});
autoUpdater.on("update-not-available", () => {
    sendStatus("Oriel is up to date.");
});
autoUpdater.on("error", err => {
    sendStatus(`Error: ${err == null ? "unknown" : err.message}`);
});
autoUpdater.on("download-progress", progressObj => {
    const msg = `Download speed: ${Math.round(progressObj.bytesPerSecond / 1024)} KB/s  
  Downloaded ${Math.round(progressObj.percent)}%`;
    sendStatus(msg);
});
autoUpdater.on("update-downloaded", () => {
    const choice = dialog.showMessageBoxSync({
        type: "question",
        buttons: ["Install and Restart", "Later"],
        title: "Update ready",
        message: "A new version of Oriel is ready to install."
    });
    if (choice === 0)
        autoUpdater.quitAndInstall();
});
function sendStatus(text) {
    if (mainWindow)
        mainWindow.webContents.send("update-message", text);
}
// ----------------------
// App lifecycle
// ----------------------
app.on("ready", () => {
    createWindow();
    // check every minute
    setInterval(() => autoUpdater.checkForUpdates(), 60000);
    autoUpdater.checkForUpdates();
});
app.on("window-all-closed", () => {
    if (process.platform !== "darwin")
        app.quit();
});
app.on("activate", () => {
    if (mainWindow === null)
        createWindow();
});
