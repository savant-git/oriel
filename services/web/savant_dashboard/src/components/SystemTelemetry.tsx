import { createSignal, onMount } from "solid-js";
export default function SystemTelemetry() {
  const [data, setData] = createSignal([]);
  onMount(async () => {
    try {
      const res = await fetch("/api/version_map.json");
      const json = await res.json();
      setData(Object.entries(json));
    } catch (e) { console.error(e); }
  });
  return (
    <section style="text-align:center;">
      <h2 style="font-family:'JetBrains Mono';font-size:1.3rem;">System Telemetry</h2>
      <table style="margin:auto;border-collapse:collapse;">
        <thead><tr><th>Module</th><th>Version</th></tr></thead>
        <tbody>
          {data().map(([file,ver])=>(
            <tr>
              <td style="padding:.3rem .8rem;border-bottom:1px solid #555;">{file}</td>
              <td style="padding:.3rem .8rem;border-bottom:1px solid #555;font-family:'JetBrains Mono';">{ver}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
