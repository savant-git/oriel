# README for `intelligence_loop.py`

## Overview

The `intelligence_loop.py` module serves as a pivotal component within the Savant ecosystem, designed to enhance the quality and completeness of Python scripts through automated analysis and improvement. By leveraging the capabilities of the OpenAI API, this module identifies incomplete or poorly documented scripts and applies enhancements to ensure they meet the standards of clarity, consistency, and safety. 

This document provides a comprehensive examination of the module, detailing its classes and functions, error-handling patterns, architectural decisions, integration points with other Savant modules, and the historical rationale behind its design.

## Core Purpose

The primary objective of `intelligence_loop.py` is to streamline the process of maintaining and improving Python scripts within the Savant framework. By automating the enhancement of code, it not only saves time for developers but also ensures that the codebase remains robust and comprehensible. This module embodies the Savant philosophy of prioritizing clarity and precision, making it an essential tool for developers working within the ecosystem.

## Detailed Analysis of Classes and Functions

The module consists of several key functions, each serving a distinct purpose:

### 1. `load_env()`

```python
def load_env():
    env_path = os.path.expanduser("~/savant/.env")
    data = {}
    with open(env_path, "r") as f:
        for line in f:
            if "=" in line:
                k, v = line.strip().split("=", 1)
                data[k.strip()] = v.strip()
    return data
```

**Purpose**: The `load_env` function is responsible for loading environment variables from a `.env` file located in the user's Savant directory. These variables typically include sensitive information such as API keys.

**Functionality**:
- It expands the user directory to locate the `.env` file.
- Reads the file line by line, splitting each line into key-value pairs.
- Returns a dictionary containing the environment variables.

**Error Handling**: The function does not currently implement explicit error handling; however, if the file does not exist or is unreadable, it will raise an `OSError`.

### 2. `call_openai(prompt, api_key, project=None)`

```python
def call_openai(prompt, api_key, project=None):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    if project:
        headers["OpenAI-Project"] = project

    body = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are a precise Python code enhancer."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }

    r = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=body)
    if r.status_code != 200:
        raise RuntimeError(f"Error code: {r.status_code} - {r.text}")
    data = r.json()
    return data["choices"][0]["message"]["content"].strip()
```

**Purpose**: This function interfaces with the OpenAI API to request enhancements for a given prompt, which typically consists of Python code.

**Functionality**:
- Constructs the request headers and body, including the prompt and model specifications.
- Sends a POST request to the OpenAI API.
- Checks the response status code and raises an error if the request fails.
- Returns the enhanced code from the API response.

**Error Handling**: The function raises a `RuntimeError` for any non-200 HTTP status codes, providing a clear message that includes the status code and response text.

### 3. `enhance_script(path, api_key, project=None)`

```python
def enhance_script(path, api_key, project=None):
    try:
        with open(path, "r", encoding="utf-8") as f:
            src = f.read()

        prompt = f"""
Enhance this Python script for completeness, consistency, and safety.
Preserve all original logic but improve structure and comments.
Return only the enhanced code.

{src}
"""
        result = call_openai(prompt, api_key, project)
        if result:
            backup = path + ".bak"
            os.rename(path, backup)
            with open(path, "w", encoding="utf-8") as f:
                f.write(result)
            footer("Complete.", "done")
        else:
            print(f"⚠ No enhancement output for → {path}")
    except Exception as e:
        print(f"❌ Enhancement failed for {path}: {e}")
```

**Purpose**: This function enhances a specified Python script by utilizing the `call_openai` function to obtain an improved version of the code.

**Functionality**:
- Reads the content of the specified script file.
- Constructs a prompt for the OpenAI API to enhance the script.
- Calls the `call_openai` function and processes the result.
- Creates a backup of the original script and writes the enhanced version to the same file.

**Error Handling**: The function includes a try-except block to handle exceptions that may arise during file operations or API calls. It reports failures with a clear message.

### 4. `run_loop(target_dir="~/savant/services")`

```python
def run_loop(target_dir="~/savant/services"):
    env = load_env()
    key = env.get("OPENAI_API_KEY")
    project = env.get("OPENAI_PROJECT_ID")

    target_dir = os.path.expanduser(target_dir)
    header("Savant Core", "1.0", "Restored aesthetic", "core")
    print(f"📂 Target directory: {target_dir}")

    incomplete = []
    for root, _, files in os.walk(target_dir):
        for f in files:
            if f.endswith(".py"):
                path = os.path.join(root, f)
                with open(path, "r", encoding="utf-8") as src:
                    content = src.read()
                    if not re.search(r'"""[\s\S]+?"""', content) or not re.search(r'\b(return|pass|def |class )', content):
                        incomplete.append(path)

    print(f"🔍 Found {len(incomplete)} incomplete scripts.")
    for fp in incomplete:
        enhance_script(fp, key, project)

    print("\n📘 Intelligence Loop finished.")
```

**Purpose**: The `run_loop` function orchestrates the overall process of scanning a target directory for Python scripts that require enhancement and invoking the enhancement process.

**Functionality**:
- Loads environment variables to retrieve the OpenAI API key and project ID.
- Expands the target directory path and prints the directory being processed.
- Walks through the directory structure to identify Python files.
- Checks each script for completeness based on the presence of docstrings and function definitions.
- Calls `enhance_script` for each incomplete script found.

**Error Handling**: The function does not explicitly handle errors related to directory access or file reading, which may need to be addressed in future iterations.

## Error-Handling Patterns and Architectural Decisions

The `intelligence_loop.py` module employs a pragmatic approach to error handling. While some functions utilize try-except blocks to catch and report exceptions, others rely on the natural propagation of errors. This design choice reflects a balance between robustness and simplicity, allowing developers to identify issues without obscuring the flow of execution.

The architectural decisions within the module are guided by the principles of modularity and separation of concerns. Each function encapsulates a specific responsibility, promoting maintainability and ease of testing. The integration of the OpenAI API exemplifies a commitment to leveraging external services to enhance functionality, while the use of environment variables underscores a focus on security and configurability.

## Integration Points with Other Savant Modules

The `intelligence_loop.py` module integrates seamlessly with other components of the Savant ecosystem. It relies on the `command_header` module for standardized output formatting, ensuring that all messages are presented consistently. Additionally, the module's use of environment variables aligns with Savant's broader strategy of managing configuration and sensitive information securely.

The enhancements provided by `intelligence_loop.py` can be utilized by other modules within Savant that require high-quality Python code. By improving the scripts, it indirectly enhances the overall performance and reliability of the entire ecosystem.

## Historical Rationale and Design Philosophy

The design of `intelligence_loop.py` is rooted in the historical context of software development, where the need for clean, maintainable code has become increasingly critical. As projects scale, the complexity of managing code quality rises, necessitating tools that can automate and streamline this process.

The module embodies the Savant philosophy of prioritizing clarity and precision in technical documentation and code. By focusing on enhancing Python scripts, it aims to elevate the overall quality of the codebase, making it easier for developers to collaborate and innovate.

Furthermore, the integration of AI-driven enhancements reflects a forward-thinking approach to software development, acknowledging the potential of artificial intelligence to augment human capabilities. This design philosophy positions `intelligence_loop.py` as a vital tool in the ongoing evolution of the Savant ecosystem.

## Conclusion

The `intelligence_loop.py` module stands as a testament to the commitment of the Savant ecosystem to uphold the highest standards of code quality and maintainability. Through its well-structured functions, thoughtful error handling, and integration with external services, it provides a powerful solution for enhancing Python scripts. As the landscape of software development continues to evolve, this module will undoubtedly play a crucial role in shaping the future of the Savant framework.