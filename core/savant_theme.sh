#!/bin/bash
# ==============================================================
# 🎨 Savant Terminal Theme — Gunmetal + Gold + Accent Edition (v310)
# ==============================================================

#   Gunmetal Light → #5C6670
#   Gunmetal Mid   → #6E7A84
#   Accent Red     → #FF4068
#   Deep Gold      → #E6C03B
#   True Gold      → #D8A200
# ==============================================================

if [[ $TERM != "xterm-256color" ]]; then
  export TERM="xterm-256color"
fi

# --- Brand Colors (lighter grays for readability) ---
GUNMETAL_LIGHT='\033[38;5;245m'
GUNMETAL_MID='\033[38;5;247m'
ACCENT_RED='\033[38;5;204m'
DEEP_GOLD='\033[38;5;220m'
TRUE_GOLD='\033[38;5;178m'
RESET='\033[0m'

# --- Prompt ---
export PS1="${TRUE_GOLD}\u${GUNMETAL_LIGHT}@${GUNMETAL_LIGHT}\h${TRUE_GOLD}:${GUNMETAL_LIGHT}\w${RESET}\$ "

clear
echo -e "${GUNMETAL_MID}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "${DEEP_GOLD}           ⚙️  Savant Environment — Gunmetal • Gold • Accent${RESET}"
echo -e "${ACCENT_RED}           $(date)${RESET}"
echo -e "${GUNMETAL_MID}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo ""
echo -e "${TRUE_GOLD}  Commands:${RESET}"
echo -e "   ${DEEP_GOLD}• savant-chat     ${GUNMETAL_LIGHT}→ Launch AI chat interface${RESET}"
echo -e "   ${DEEP_GOLD}• savant-archive  ${GUNMETAL_LIGHT}→ Run extract + export pipeline${RESET}"
echo -e "   ${DEEP_GOLD}• savant-export   ${GUNMETAL_LIGHT}→ Export system state${RESET}"
echo -e "   ${DEEP_GOLD}• savant-clean    ${GUNMETAL_LIGHT}→ Clean caches and logs${RESET}"
echo -e "   ${DEEP_GOLD}• savant-cd       ${GUNMETAL_LIGHT}→ Jump to ~/savant${RESET}"
echo -e "   ${DEEP_GOLD}• savant-rules    ${GUNMETAL_LIGHT}→ View PROJECT_RULES.md${RESET}"
echo -e "   ${DEEP_GOLD}• savant-reload   ${GUNMETAL_LIGHT}→ Reload environment${RESET}"
echo ""
echo -e "${GUNMETAL_MID}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo ""

# --- Rule Hash Indicator ---
RULE_FILE="$HOME/savant/docs/PROJECT_RULES.md"
if [[ -f "$RULE_FILE" ]]; then
  HASH=$(sha256sum "$RULE_FILE" | cut -c1-10)
  echo -e "${TRUE_GOLD}🧩 PROJECT_RULES.md validated — hash: ${ACCENT_RED}${HASH}${RESET}"
else
  echo -e "${ACCENT_RED}⚠️  PROJECT_RULES.md missing — enforcement suspended.${RESET}"
fi
echo ""
