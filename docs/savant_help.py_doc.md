# README for `savant_help.py`

## Overview

The `savant_help.py` module serves as a pivotal component within the Savant ecosystem, designed to provide users with an intuitive and dynamic help system. This module generates a comprehensive, color-coded index of all Savant commands, pulling relevant information from various sources, including user-defined aliases, documentation files, and version information. By consolidating this data, `savant_help.py` enhances user experience and accessibility, ensuring that users can quickly find and utilize the commands available to them.

## Core Purpose

The core purpose of `savant_help.py` is to facilitate user interaction with the Savant framework by dynamically generating a command index. This index groups commands by their respective subsystems, allowing users to navigate the available functionalities effortlessly. The module achieves this by:

1. **Extracting Aliases**: It retrieves command aliases defined in the user's `.bashrc` file, enabling users to execute Savant commands with ease.
2. **Documenting Commands**: It pulls metadata from markdown documentation files located in the `docs` directory, providing users with descriptive summaries of each command.
3. **Version Control**: It integrates version information from the Savant version engine, ensuring that users are aware of the versions of the commands they are using.

By combining these elements, `savant_help.py` not only serves as a reference guide but also as a tool for enhancing the overall usability of the Savant system.

## Detailed Analysis of Classes and Functions

### Imports and Global Variables

```python
from savant.services.scripts.system_core.command_header import header, footer
import os, re, sys, textwrap
from pathlib import Path
from datetime import datetime, timezone
from rich.console import Console
from rich.table import Table
from rich.theme import Theme
```

The module begins by importing necessary libraries and defining global variables. The use of the `rich` library allows for enhanced console output, including color-coded themes and formatted tables.

- **ROOT**: Points to the home directory of the Savant framework.
- **DOCS**: Points to the documentation directory.
- **BASHRC**: Points to the user's `.bashrc` file.
- **console**: An instance of `Console` from the `rich` library, configured with a custom theme for various command categories.

### Functions

#### `extract_docs(name: str)`

```python
def extract_docs(name: str):
    path = DOCS / f"{name}.py_doc.md"
    if not path.exists():
        alt = DOCS / f"{name}_doc.md"
        if not alt.exists():
            return "No documentation found."
        path = alt
    text = path.read_text(errors="ignore")
    summary = textwrap.shorten(" ".join(text.split()[:80]), width=300)
    return summary
```

- **Purpose**: Extracts documentation for a given command from markdown files.
- **Parameters**: `name` - The name of the command for which documentation is sought.
- **Returns**: A summary of the documentation or a message indicating that no documentation was found.
- **Error Handling**: Utilizes a fallback mechanism to check for alternative documentation files if the primary file does not exist.

#### `guess_category(script: str)`

```python
def guess_category(script: str):
    script = script.lower()
    if "ai" in script or "personality" in script: return "ai"
    if "cluster" in script or "intelligence" in script: return "cluster"
    if "engine" in script: return "engine"
    if "guard" in script or "rule" in script: return "guardian"
    return "utility"
```

- **Purpose**: Infers the category of a command based on its name.
- **Parameters**: `script` - The command name.
- **Returns**: A string representing the category (e.g., "ai", "cluster", "engine", "guardian", "utility").
- **Error Handling**: No explicit error handling; however, it defaults to "utility" if no matches are found.

#### `load_aliases()`

```python
def load_aliases():
    aliases = []
    for line in BASHRC.read_text().splitlines():
        m = re.match(r"alias (savant-[a-z0-9_-]+)='python3 (.+)'", line)
        if m: aliases.append((m.group(1), Path(m.group(2)).name))
    return aliases
```

- **Purpose**: Loads command aliases from the user's `.bashrc` file.
- **Returns**: A list of tuples containing command aliases and their corresponding script names.
- **Error Handling**: Does not explicitly handle errors; assumes the `.bashrc` file is formatted correctly.

#### `load_versions()`

```python
def load_versions():
    meta = {}
    vm = ROOT / "services/scripts/version_engine/version_map.json"
    if vm.exists():
        try:
            import json; meta = json.loads(vm.read_text())
        except: pass
    return meta
```

- **Purpose**: Loads version information from a JSON file.
- **Returns**: A dictionary containing version metadata.
- **Error Handling**: Uses a try-except block to handle potential JSON parsing errors gracefully.

#### `main()`

```python
def main():
    aliases = load_aliases()
    versions = load_versions()
    if not aliases:
        console.footer("Error.", "error")
        sys.exit(0)

    table = Table(title=f"SAVANT COMMAND INDEX — {datetime.now().strftime('%Y-%m-%d %H:%M')}", show_lines=True)
    table.add_column("Command", style="header", no_wrap=True)
    table.add_column("Subsystem", style="header")
    table.add_column("Version", style="version")
    table.add_column("Description", style="header")

    for cmd, script in sorted(aliases):
        cat = guess_category(script)
        summary = extract_docs(script)
        version = "—"
        if script in versions:
            version = versions[script].get("version", "—")
        table.add_row(cmd, cat, version, summary, style=cat)

    console.print(table)
    console.print("\n[bold white]Tip:[/] Run [yellow]savant-docs[/] to regenerate documentation.")
    console.print("[bold white]Usage:[/] Type [cyan]savant-[command][/cyan] to execute a module.\n")
```

- **Purpose**: The primary entry point of the module, orchestrating the loading of aliases, versions, and the generation of the command index table.
- **Error Handling**: Checks if no aliases are found and gracefully exits with an error message.

## Error-Handling Patterns and Architectural Decisions

The error-handling patterns within `savant_help.py` are designed to ensure a seamless user experience while maintaining robustness. The module employs several strategies:

1. **Fallback Mechanisms**: The `extract_docs` function includes a fallback to check for alternative documentation files if the primary file is not found. This ensures that users are less likely to encounter a complete failure due to missing documentation.

2. **Graceful Exits**: In the `main` function, if no aliases are found, the program exits gracefully with an error message, preventing further execution that could lead to confusion or crashes.

3. **Try-Except Blocks**: The `load_versions` function utilizes a try-except block to handle potential errors during JSON parsing, allowing the program to continue running even if version information is unavailable.

These architectural decisions reflect a commitment to user-centric design, ensuring that the module remains functional and informative even in the face of potential issues.

## Integration Points with Other Savant Modules

`savant_help.py` is intricately integrated with various components of the Savant ecosystem, enhancing its functionality and user experience:

1. **Command Aliases**: By reading aliases from the user's `.bashrc`, the module interacts with the user's shell environment, allowing for seamless command execution.

2. **Documentation Files**: The module pulls metadata from markdown documentation files located in the `docs` directory. This integration ensures that users have access to the most up-to-date information about each command.

3. **Version Engine**: The module interfaces with the version engine to retrieve version information, providing users with insights into the specific versions of commands they are using.

These integration points not only enhance the functionality of `savant_help.py` but also contribute to the overall coherence and usability of the Savant framework.

## Historical Rationale and Design Philosophy

The design of `savant_help.py` is rooted in the historical context of the Savant framework's development. As the framework evolved, the need for a robust help system became evident. Users required a means to navigate the expanding array of commands and functionalities without becoming overwhelmed.

The decision to create a dynamic, command-based help system was driven by several key principles:

1. **User-Centric Design**: The module prioritizes user experience by providing a clear and accessible command index, allowing users to quickly locate and understand the commands at their disposal.

2. **Modularity**: The design embraces modularity, allowing for easy integration with other components of the Savant ecosystem. This approach facilitates future enhancements and expansions of the help system.

3. **Simplicity and Clarity**: The use of rich formatting and color coding enhances the clarity of the output, making it visually appealing and easier to digest.

4. **Robustness**: The inclusion of error-handling mechanisms ensures that the module remains functional and informative, even in the face of potential issues.

In conclusion, `savant_help.py` stands as a testament to the Savant framework's commitment to providing users with an intuitive and effective means of navigating its commands. Through careful design and integration, the module enhances the overall usability of the Savant ecosystem, ensuring that users can harness the full potential of the framework with confidence and ease.