import os from "node:os";
try { os.cpus(); } catch {
  (os as any).cpus = () => [{ model: "TermuxVirtualCore", speed: 1200 }];
}
