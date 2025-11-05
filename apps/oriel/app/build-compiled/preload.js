/**
 * preload.ts
 * Secure bridge between Electron main process and renderer (UI)
 *
 * Exposes limited, safe APIs that the front-end can call.
 */
import { contextBridge, ipcRenderer } from "electron";
contextBridge.exposeInMainWorld("OrielAPI", {
    /** Listen for update messages from main.ts (auto-updater) */
    onUpdateMessage: (callback) => {
        ipcRenderer.on("update-message", (_event, message) => {
            callback(message);
        });
    },
    /** Send arbitrary commands to the main process if needed */
    sendCommand: (cmd, arg) => {
        ipcRenderer.send("oriel-cmd", { cmd, arg });
    },
    /** Optional helper to remove listeners when closing UI */
    removeAllUpdateListeners: () => {
        ipcRenderer.removeAllListeners("update-message");
    }
});
