import { onMount, createSignal } from "solid-js";
export default function ContextLedgerVisualizer() {
  const [ledger, setLedger] = createSignal([]);
  onMount(async () => {
    try {
      const res = await fetch("/api/context_ledger.json");
      const json = await res.json();
      setLedger(json.entries || []);
    } catch (e) { console.error(e); }
  });
  return (
    <section style="margin-top:2rem;text-align:center;">
      <h2 style="font-family:'JetBrains Mono';font-size:1.3rem;">Context Ledger</h2>
      <table style="margin:auto;border-collapse:collapse;">
        <thead><tr><th>Timestamp</th><th>Event</th><th>Status</th></tr></thead>
        <tbody>
          {ledger().map(e=>(
            <tr>
              <td style="padding:.4rem;border-bottom:1px solid #555;">{e.timestamp}</td>
              <td style="padding:.4rem;border-bottom:1px solid #555;">{e.event}</td>
              <td style="padding:.4rem;border-bottom:1px solid #555;">{e.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
