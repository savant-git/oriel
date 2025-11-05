# README for `docsynth_daemon.py`

## Overview

The `docsynth_daemon.py` module serves as an integral component of the Savant ecosystem, functioning as an autonomous documentation and comment synchronization engine. It is designed to enhance the maintainability and usability of the Savant codebase by automatically generating and updating detailed README files for each Python script within the ecosystem. This module not only ensures that documentation is current but also injects insightful technical commentary into the code itself, fostering a culture of clarity and understanding among developers.

This document provides a comprehensive analysis of the `docsynth_daemon.py` module, detailing its core purpose, internal architecture, error-handling strategies, integration points with other Savant modules, and the historical rationale behind its design.

## Core Purpose

The primary function of `docsynth_daemon.py` is to automate the generation of documentation and comments for the Savant project. By performing routine scans of all Python scripts, it accomplishes the following tasks:

1. **Documentation Generation**: It creates or updates markdown README files, ensuring they are approximately 2500 words in length and contain detailed descriptions of each module's purpose, classes, functions, error-handling patterns, architectural decisions, integration points, and design philosophy.

2. **Comment Injection**: The module injects standardized commentary blocks into the source code, providing context and insights about the purpose and functionality of classes and functions.

3. **Metadata Synchronization**: It syncs relevant metadata for the Savant help system, ensuring that all documentation is consistent and up-to-date.

By automating these processes, `docsynth_daemon.py` significantly reduces the manual effort required to maintain documentation, thereby allowing developers to focus on writing code rather than documenting it.

## Detailed Analysis of Classes and Functions

### Imports

The module begins by importing necessary libraries and modules:

```python
import os, re, time, json, textwrap, openai
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv
```

- **os**: Provides a way to use operating system-dependent functionality.
- **re**: Enables regular expression operations for text processing.
- **time**: Facilitates time-related functions, including sleep.
- **json**: Allows for JSON manipulation, though not explicitly used in the provided code.
- **textwrap**: Provides text wrapping and filling functionality.
- **openai**: Interfaces with the OpenAI API for generating documentation text.
- **datetime**: Handles date and time operations.
- **pathlib**: Offers an object-oriented interface for filesystem paths.
- **dotenv**: Loads environment variables from a `.env` file.

### Constants

The module defines several constants that establish paths for the Savant project:

```python
ROOT = Path.home() / "savant"
DOCS = ROOT / "docs"
LOG = ROOT / "logs" / "docsynth_daemon.log"
```

- **ROOT**: The base directory for the Savant project.
- **DOCS**: The directory where generated documentation files are stored.
- **LOG**: The path for the log file that records the daemon's activities.

### Environment Variables

The module loads environment variables to configure the OpenAI API key:

```python
load_dotenv(ROOT / ".env")
openai.api_key = os.getenv("OPENAI_API_KEY")
```

This allows the module to authenticate with the OpenAI service for documentation generation.

### Functions

#### `log(msg: str)`

This function logs messages to a specified log file, including timestamps:

```python
def log(msg: str):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG, "a") as f:
        f.write(f"[{datetime.now(timezone.utc).isoformat()}] {msg}\n")
```

- **Parameters**: 
  - `msg`: A string message to be logged.
  
- **Behavior**: 
  - Creates the log directory if it does not exist.
  - Appends the message to the log file with a timestamp.

#### `summarize_file(path: Path) -> str`

This function reads the first 400 lines of a given Python script and returns it as a string:

```python
def summarize_file(path: Path) -> str:
    try:
        txt = path.read_text(errors="ignore")
        return "\n".join(txt.splitlines()[:400])
    except Exception as e:
        return f"<error reading {path}: {e}>"
```

- **Parameters**: 
  - `path`: The path to the Python script.
  
- **Returns**: 
  - A string containing the first 400 lines of the script or an error message if reading fails.

#### `generate_docs(script_path: Path)`

This function generates documentation for a specific script:

```python
def generate_docs(script_path: Path):
    name = script_path.name
    context = summarize_file(script_path)
    prompt = f"""
    You are Savant, a precise documentation AI.
    Provide an approximately 2500-word README describing the module '{name}'.
    ...
    """
    try:
        resp = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are Savant, a world-class technical documentarian."},
                {"role": "user", "content": prompt + "\n\nCode excerpt:\n" + context}
            ],
            temperature=0.4
        )
        text = resp.choices[0].message.content.strip()
        DOCS.mkdir(parents=True, exist_ok=True)
        out = DOCS / f"{name}_doc.md"
        out.write_text(text, encoding="utf-8")
        log(f"✅ README updated for {name}")
    except Exception as e:
        log(f"❌ README generation failed for {name}: {e}")
```

- **Parameters**: 
  - `script_path`: The path to the Python script for which documentation is generated.
  
- **Behavior**: 
  - Summarizes the script and constructs a prompt for the OpenAI model.
  - Calls the OpenAI API to generate a README.
  - Writes the generated README to the appropriate directory.
  - Logs success or failure.

#### `inject_comments(script_path: Path)`

This function injects comments into the source code of a given script:

```python
def inject_comments(script_path: Path):
    text = script_path.read_text(errors="ignore")
    if "### — Savant Insight —" in text:
        return
    comments = []
    for m in re.finditer(r"^(class|def)\s+([A-Za-z0-9_]+)", text, re.M):
        block = f"### — Savant Insight —\n# Purpose: {m.group(2)} — auto-annotated by Savant DocSynth\n# Added {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        comments.append((m.start(), block))
    for offset, block in reversed(comments):
        text = text[:offset] + block + text[offset:]
    script_path.write_text(text, encoding="utf-8")
    log(f"🧩 Comments injected into {script_path.name}")
```

- **Parameters**: 
  - `script_path`: The path to the Python script where comments will be injected.
  
- **Behavior**: 
  - Reads the script and checks for existing comments.
  - Uses regular expressions to find class and function definitions.
  - Constructs a comment block for each definition and injects it into the script.
  - Writes the updated script back to the file.

#### `sync_all()`

This function synchronizes documentation and comments for all relevant scripts:

```python
def sync_all():
    count = 0
    for script in (ROOT / "services").rglob("*.py"):
        if "__init__" in script.name:
            continue
        inject_comments(script)
        generate_docs(script)
        count += 1
    log(f"✅ Sync complete for {count} modules.")
    footer("Complete.", "done")
```

- **Behavior**: 
  - Iterates through all Python scripts in the services directory.
  - Skips `__init__.py` files.
  - Calls `inject_comments` and `generate_docs` for each script.
  - Logs the number of modules processed.

#### `main()`

The main entry point for the module:

```python
def main():
    header("Savant Core", "1.0", "Restored aesthetic", "core")
    while True:
        sync_all()
        log("⏳ Sleeping for 24 hours.")
        time.sleep(86400)
```

- **Behavior**: 
  - Initializes the logging header.
  - Enters an infinite loop where it synchronizes documentation and comments every 24 hours.

## Error-Handling Patterns

The `docsynth_daemon.py` module employs a straightforward error-handling strategy primarily through the use of try-except blocks. This pattern is evident in the `summarize_file`, `generate_docs`, and `inject_comments` functions, where potential exceptions are caught, and appropriate error messages are logged without interrupting the daemon's overall operation.

For instance, in the `generate_docs` function, if the OpenAI API call fails, the error is logged, allowing the daemon to continue processing other scripts rather than terminating abruptly. This design choice reflects a commitment to reliability and robustness, ensuring that the documentation process remains resilient in the face of unexpected issues.

## Architectural Decisions

The architecture of `docsynth_daemon.py` is characterized by its modular design and separation of concerns. Each function has a clearly defined responsibility, facilitating easier maintenance and testing. The use of regular expressions for comment injection allows for flexible and powerful text manipulation, while the integration with the OpenAI API exemplifies a forward-thinking approach to leveraging AI in software development.

The decision to use a continuous loop for the main execution flow aligns with the goal of maintaining up-to-date documentation. By running the synchronization process every 24 hours, the module ensures that the documentation evolves alongside the codebase, reflecting the latest changes and insights.

## Integration Points with Other Savant Modules

The `docsynth_daemon.py` module integrates seamlessly with other components of the Savant ecosystem. It relies on the `header` and `footer` functions from the `savant.services.scripts.system_core.command_header` module to manage logging output, providing a consistent user experience across the Savant tools.

Additionally, the module's output—markdown README files—serves as a critical resource for developers working with the Savant codebase, enhancing their understanding of the modules and facilitating better collaboration. The injected comments also play a vital role in code maintainability, offering immediate context to developers reviewing or modifying the code.

## Historical Rationale and Design Philosophy

The development of `docsynth_daemon.py` was driven by the recognition that documentation is often neglected in software projects, leading to increased onboarding time for new developers and a higher likelihood of misunderstandings within the codebase. By automating the documentation process, the Savant team aimed to create a culture of clarity and transparency, where documentation is not an afterthought but an integral part of the development workflow.

The design philosophy behind this module emphasizes simplicity, reliability, and usability. The straightforward logging mechanism, the clear separation of functionality, and the use of AI for documentation generation all reflect a commitment to enhancing the developer experience. By reducing the burden of documentation, `docsynth_daemon.py` allows developers to focus on what they do best: writing code.

## Conclusion

The `docsynth_daemon.py` module is a pivotal element of the Savant ecosystem, embodying a forward-thinking approach to documentation and code maintainability. Through its automated processes, it not only generates comprehensive documentation but also enriches the codebase with insightful commentary. By embracing automation and AI, the Savant team has set a new standard for documentation practices, ensuring that clarity and understanding remain at the forefront of software development.