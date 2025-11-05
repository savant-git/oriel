import { createSignal, onMount } from "solid-js";
import { animate, spring } from "motion";

export default function Dashboard() {
  const [ready, setReady] = createSignal(false);
  onMount(() => {
    animate("h1", { opacity: [0, 1], y: [-25, 0] }, { duration: 1.2, easing: spring() });
    setTimeout(() => setReady(true), 1200);
  });

  return (
    <main style="text-align:center;padding:2rem;">
      <h1>Savant Development Dashboard</h1>
      <p style="opacity:.75;margin-bottom:1rem;">Version grid: Shard Map initialization</p>
      <canvas id="shard-map" width="600" height="400"
        style="margin:auto;border:1px solid var(--gold-dark);border-radius:8px;"></canvas>
      {ready()
        ? <p style="color:var(--gold);margin-top:1rem;">Active modules loaded.</p>
        : <p style="color:var(--gold-dark);margin-top:1rem;">Initializing…</p>}
    </main>
  );
}
