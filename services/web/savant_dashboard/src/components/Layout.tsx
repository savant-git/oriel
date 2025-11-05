import { ParentProps } from "solid-js";
export default function Layout(props: ParentProps) {
  return (
    <div style={{
      "background":"#1e1e21",
      "color":"#e4c66f",
      "font-family":"'Inter', sans-serif",
      "min-height":"100vh",
      "display":"flex",
      "flex-direction":"column",
      "align-items":"center"
    }}>
      <header style="border-bottom:1px solid #8a742b66;width:100%;padding:1rem;text-align:center;">
        <h1 style="font-family:'JetBrains Mono';letter-spacing:0.05em;">Savant Dashboard</h1>
      </header>
      <main style="flex:1;width:100%;max-width:1200px;padding:2rem;">{props.children}</main>
      <footer style="border-top:1px solid #8a742b66;padding:.5rem;text-align:center;font-size:.8rem;opacity:.5;">
        Savant v7.2 (♦15>12 | ⬣13=10 | ⬡11<9)
      </footer>
    </div>
  );
}
