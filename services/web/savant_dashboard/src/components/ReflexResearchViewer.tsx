import { createSignal, onMount } from "solid-js";
export default function ReflexResearchViewer() {
  const [entries, setEntries] = createSignal([]);
  onMount(async () => {
    try {
      const res = await fetch("/api/research_index.json");
      const json = await res.json();
      setEntries(json.entries || []);
    } catch (e) { console.error("Research load error", e); }
  });
  return (
    <section style="margin-top:2rem;text-align:center;">
      <h2 style="font-family:'JetBrains Mono';font-size:1.3rem;">Reflex Research Log</h2>
      <div style="max-height:300px;overflow:auto;border:1px solid #8a742b33;padding:1rem;border-radius:0.5rem;text-align:left;">
        {entries().map(e=>(
          <article style="margin-bottom:1rem;">
            <div style="opacity:.6;font-size:.8rem;">{e.timestamp}</div>
            <strong>{e.topic}</strong>
            <p style="margin:0.25rem 0 0.75rem 0;">{e.summary.slice(0,150)}...</p>
          </article>
        ))}
      </div>
    </section>
  );
}
