#!/usr/bin/env python3
"""
savant-chat — safe local code analyzer / upgrader
Compatible with openai>=1.0.0
"""

import os
from openai import OpenAI
from dotenv import load_dotenv
from colorama import init, Fore, Style

# -------------------- setup --------------------
init(autoreset=True)
BASE = os.path.expanduser("~/savant")
ENV_PATH = os.path.join(BASE, ".env")
if os.path.exists(ENV_PATH):
    load_dotenv(ENV_PATH)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

GOLD = Fore.YELLOW + Style.BRIGHT
GRAY = Fore.LIGHTBLACK_EX
RESET = Style.RESET_ALL

def read_file(path: str) -> str:
    abs_path = os.path.abspath(os.path.expanduser(path))
    if not abs_path.startswith(BASE):
        raise PermissionError("Access limited to ~/savant")
    with open(abs_path, "r", encoding="utf-8") as file:
        return file.read()

def ask_openai(prompt: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system",
             "content": "You are the Savant AI Core. Improve or refactor code safely and clearly. "
                        "Output only the complete rewritten code."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=3000,
    )
    return response.choices[0].message.content.strip()

def optimize(path: str, versions: int = 1):
    code = read_file(path)
    message = (
        f"Hypothetically optimize or refactor the following code {versions} version(s) ahead. "
        f"Preserve its purpose and readability.\n\n{code}"
    )
    result = ask_openai(message)
    print(f"{GOLD}--- Optimized code ---{RESET}\n{result}")

# -------------------- interface --------------------
def main():
    print(f"{GOLD}🧠 SAVANT CHAT{RESET} — {GRAY}Code optimization console{RESET}")
    print("Commands:")
    print(f"{GOLD}:optimize <path>{RESET}       optimize code one version ahead")
    print(f"{GOLD}:upgrade <path> <n>{RESET}    show hypothetical upgrade n versions ahead")
    print(f"{GOLD}:exit{RESET}                  quit\n")

    while True:
        try:
            cmd = input(f"{GOLD}> {RESET}").strip()
            if not cmd:
                continue
            if cmd.lower() in {":exit", "exit"}:
                print(f"{GRAY}Session ended.{RESET}")
                break

            parts = cmd.split()
            if parts[0] == ":optimize" and len(parts) >= 2:
                optimize(parts[1])
                continue
            if parts[0] == ":upgrade" and len(parts) >= 3:
                try:
                    n = int(parts[2])
                except ValueError:
                    n = 1
                optimize(parts[1], n)
                continue

            # default: chat mode
            response = ask_openai(cmd)
            print(f"{GRAY}{response}{RESET}")

        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
