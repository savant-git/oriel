/** @type {import('tailwindcss').Config} */
export default {
  content: ["./src/**/*.{html,js,svelte,ts}"],
  theme: {
    extend: {
      colors: {
        gunmetal: { light:"#2e2e32", DEFAULT:"#1e1e21", dark:"#0e0e10" },
        gold: { light:"#e4c66f", DEFAULT:"#c7a740", dark:"#8a742b" }
      },
      boxShadow: { glow:"0 0 25px rgba(200,167,64,0.25)" },
      fontFamily: { sans:["Inter","sans-serif"], mono:["JetBrains Mono","monospace"] }
    }
  },
  plugins: []
};
