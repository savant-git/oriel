from savant.core.savant_console_theme import console, header, divider, rule_status, success, error, accent
#!/usr/bin/env python3
"""
💬 Savant Chat Interface v120
"""
import os, openai, readline
from rich.console import Console
from rich.panel import Panel
from dotenv import load_dotenv

load_dotenv(os.path.expanduser("~/savant/.env"))
openai.api_key = os.getenv("OPENAI_API_KEY")
console = Console()

def chat():
    console.console.print(Panel.fit("💬 [bold cyan]Savant Chat Interface v120[/bold cyan]\nType 'exit' to quit.", style="cyan"))
    messages = [{"role":"system","content":"You are Savant, a precise AI assistant bound by all project rules."}]
    while True:
        prompt = console.input("[bold green]🧠 You:[/bold green] ")
        if prompt.strip().lower() in ["exit","quit"]: break
        try:
            completion = openai.ChatCompletion.create(model="gpt-4o-mini", messages=messages+[{"role":"user","content":prompt}])
            reply = completion.choices[0].message["content"]
            console.console.print(Panel(reply, title="Savant", style="bold blue"))
            messages.append({"role":"user","content":prompt})
            messages.append({"role":"assistant","content":reply})
        except Exception as e:
            console.console.print(f"[red]⚠️ Error:[/red] {e}")

if __name__ == "__main__":
    chat()
