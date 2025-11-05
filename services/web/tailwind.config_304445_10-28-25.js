/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,jsx,ts,tsx}",
    "./components/**/*.{js,jsx,ts,tsx}",
    "./pages/**/*.{js,jsx,ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        gunmetal: {
          light: "#2b2b2e",
          DEFAULT: "#18181a",
          dark: "#0e0e10",
        },
        gold: {
          light: "#f0d478",
          DEFAULT: "#c7a740",
          dark: "#8a742b",
        },
        red: {
          shard: "#b43636",
        },
      },
      boxShadow: {
        glow: "0 0 20px rgba(199,167,64,0.25)",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
    },
  },
  plugins: [],
}
