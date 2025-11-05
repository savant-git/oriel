import { createGlobalTheme } from "@vanilla-extract/css";
export const vars = createGlobalTheme(":root", {
  color: {
    gunmetal: "#1e1e21",
    gold: "#c7a740",
    goldLight: "#e4c66f",
    goldDeep: "#8a742b"
  },
  font: {
    sans: "'Inter', sans-serif",
    mono: "'JetBrains Mono', monospace"
  }
});
