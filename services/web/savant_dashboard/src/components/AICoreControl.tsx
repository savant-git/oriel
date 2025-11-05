import { createSignal } from "solid-js";
export default function AICoreControl() {
  const [prompt, setPrompt] = createSignal("");
  const [reply, setReply] = createSignal("");
  async function sendPrompt() {
    setReply("⏳ Processing...");
    try {
      const res = await fetch("/api/ai_core.json", {
        method:"POST",
        headers:{ "Content-Type":"application/json" },
        body:JSON.stringify({ prompt:prompt() })
      });
      const data = await res.json();
      setReply(data.response || "⚠️ No response");
    } catch (e) {
      setReply("❌ Error: "+e.message);
    }
  }
  return (
    <section style="margin-top:2rem;text-align:center;">
      <h2 style="font-family:'JetBrains Mono';font-size:1.3rem;">AI Core Control</h2>
      <textarea style="width:80%;height:80px;background:#2e2e32;color:#e4c66f;border:1px solid #8a742b66;padding:.5rem;"
        onInput={(e)=>setPrompt(e.currentTarget.value)} placeholder="Enter prompt..." />
      <br/>
      <button style="margin-top:.5rem;padding:.4rem 1rem;background:#8a742b33;border:1px solid #8a742b66;border-radius:.3rem;color:#e4c66f;"
        onClick={sendPrompt}>Run</button>
      <pre style="margin-top:1rem;background:#121213;color:#e4c66f;padding:1rem;border-radius:.5rem;text-align:left;max-width:80%;overflow:auto;">
        {reply()}
      </pre>
    </section>
  );
}
