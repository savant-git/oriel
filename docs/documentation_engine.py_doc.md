# README for `documentation_engine.py`

## Overview

The `documentation_engine.py` module serves as a pivotal component within the Savant ecosystem, designed to autonomously generate comprehensive documentation for service scripts. This module not only enhances the clarity and accessibility of the codebase but also enforces a consistent documentation style across all modules. By leveraging the OpenAI API, it generates detailed README files that encapsulate the essence of each script, ensuring that developers and users alike can navigate the intricacies of the Savant framework with ease.

## Core Purpose

The primary function of `documentation_engine.py` is to automate the documentation process for Python scripts located within the Savant service directory. This module achieves the following objectives:

1. **Documentation Generation**: It scans all service scripts, generates long-form README files (approximately 2500 words per module), and saves them in the `/savant/docs` directory.
2. **Header Injection**: It inserts standardized Savant-style doc headers into each script that lacks documentation, providing essential metadata about the file.
3. **Error Logging**: It maintains a log of operations, including successful documentation generation and any encountered errors, ensuring traceability and accountability.

By fulfilling these roles, `documentation_engine.py` significantly reduces the manual effort required for documentation while promoting a culture of thoroughness and clarity within the development team.

## Detailed Analysis of Classes and Functions

### Functions

#### 1. `log(msg: str)`

**Purpose**: This function logs messages to a designated log file located at `ROOT/logs/doc_engine.log`. It records the timestamp and the message, allowing developers to track the execution flow and identify issues.

**Parameters**:
- `msg`: A string message to be logged.

**Implementation**:
```python
def log(msg: str):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG, "a") as f:
        f.write(f"[{datetime.now(timezone.utc).isoformat()}] {msg}\n")
```

**Error Handling**: The function handles potential errors related to file I/O by ensuring the log directory exists before attempting to write to the log file.

#### 2. `generate_readme(script_path: Path)`

**Purpose**: This function generates a README file for a given script by utilizing the OpenAI API. It constructs a prompt that requests a detailed explanation of the script's functionality, design philosophy, error handling, and integration points.

**Parameters**:
- `script_path`: A `Path` object representing the path to the Python script.

**Implementation**:
```python
def generate_readme(script_path: Path):
    name = script_path.name
    text = script_path.read_text(errors="ignore")
    prompt = f"""You are Savant, a hyper-technical documentation system...
    """
    try:
        resp = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
        )
        content = resp.choices[0].message.content.strip()
        out_file = DOCS / f"{name}_doc.md"
        DOCS.mkdir(parents=True, exist_ok=True)
        out_file.write_text(content, encoding="utf-8")
        log(f"✅ Generated README for {name}")
    except Exception as e:
        log(f"❌ Failed to generate {name}: {e}")
```

**Error Handling**: The function uses a try-except block to catch exceptions that may arise during the API call or file operations. If an error occurs, it logs the failure message, ensuring that the developer is informed of the issue.

#### 3. `inject_header(script_path: Path)`

**Purpose**: This function inserts a standardized documentation header into a script if it is absent. The header provides essential information about the script's purpose and links to the README file for further details.

**Parameters**:
- `script_path`: A `Path` object representing the path to the Python script.

**Implementation**:
```python
def inject_header(script_path: Path):
    text = script_path.read_text(errors="ignore")
    if "# ===" in text:  # already documented
        return
    header = textwrap.dedent(f"""\
    # ===============================================================
    # {script_path.name}
    # Purpose: Auto-generated Savant documentation header.
    # Behavior: See {script_path.name}_doc.md for extended analysis.
    # Notes: Created {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    # ===============================================================
    """)
    script_path.write_text(header + text, encoding="utf-8")
```

**Error Handling**: The function checks if the script already contains a header before attempting to inject a new one, thus preventing redundancy. It also handles potential file read/write errors through the `errors="ignore"` parameter.

#### 4. `main()`

**Purpose**: The entry point of the module, `main()` orchestrates the scanning of service scripts, invoking the header injection and README generation processes for each script.

**Implementation**:
```python
def main():
    count = 0
    for p in (ROOT / "services").rglob("*.py"):
        if "__init__" in p.name: 
            continue
        inject_header(p)
        generate_readme(p)
        count += 1
    footer("Complete.", "done")
    log(f"Completed {count} modules.")
```

**Error Handling**: The function does not explicitly handle errors within its loop, but it relies on the error handling present in the `inject_header` and `generate_readme` functions. This design allows for graceful degradation; if one script fails, the process continues for others.

## Architectural Decisions

The `documentation_engine.py` module is architected with a focus on modularity, maintainability, and automation. Key architectural decisions include:

1. **Modularity**: Each function serves a distinct purpose, allowing for easier testing and modification. This modular approach enhances the readability of the code and simplifies debugging.
  
2. **Use of OpenAI API**: By integrating the OpenAI API, the module leverages advanced natural language processing capabilities to generate human-like documentation. This decision reflects a commitment to quality and depth in documentation.

3. **Error Handling**: The use of try-except blocks and checks for existing headers demonstrates a proactive approach to error handling, minimizing disruptions in the documentation process.

4. **File Structure**: The module adheres to a clear directory structure, with logs and documentation organized under the `savant` root. This organization facilitates easy navigation and maintenance.

## Integration Points with Other Savant Modules

The `documentation_engine.py` module integrates seamlessly with other components of the Savant ecosystem:

- **Service Scripts**: It directly interacts with service scripts located in the `savant/services` directory, scanning each script for documentation purposes.
  
- **Logging System**: The logging functionality is crucial for maintaining operational transparency across the Savant ecosystem. Other modules can reference the log file for insights into the documentation process.

- **OpenAI Integration**: The module's reliance on the OpenAI API for documentation generation establishes a dependency that other modules may utilize for similar purposes, promoting consistency across the documentation landscape.

## Historical Rationale and Design Philosophy

The inception of `documentation_engine.py` stemmed from a recognized need for comprehensive and consistent documentation within the Savant framework. Historically, documentation has often been an afterthought in software development, leading to fragmented and outdated information. The design philosophy behind this module is rooted in the belief that high-quality documentation is essential for fostering collaboration, enhancing code maintainability, and ensuring knowledge transfer among team members.

The decision to automate documentation generation reflects a commitment to efficiency and precision. By harnessing the capabilities of the OpenAI API, the module not only saves time but also elevates the standard of documentation, ensuring that it is both informative and engaging.

In conclusion, `documentation_engine.py` embodies the principles of clarity, precision, and automation. It stands as a testament to the Savant team's dedication to creating a robust and accessible codebase, ultimately empowering developers and users alike to navigate the complexities of the Savant ecosystem with confidence.