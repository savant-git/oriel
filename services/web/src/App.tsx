import { createSignal, onMount } from "solid-js";
import { animate } from "motion";
import * as THREE from "three";

export default function App() {
  const [ready, setReady] = createSignal(false);
  onMount(() => {
    animate("h1", { opacity: [0, 1], y: [-30, 0] }, { duration: 1 });
    setTimeout(()=>setReady(true),800);
  });
  return (
    <main style="background:#1e1e21;color:#e4c66f;text-align:center;min-height:100vh;padding:2rem;">
      <h1 style="font-family:'JetBrains Mono'">Savant Dashboard</h1>
      <p>Phase 150 · Bun Runtime Active</p>
      {ready()
        ? <p>🧠 Loaded — System stable.</p>
        : <p>⚙️ Initializing environment…</p>}
    </main>
  );
}
