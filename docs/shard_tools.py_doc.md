# README for `shard_tools.py`

## Overview

The `shard_tools.py` module is a critical component of the Savant ecosystem, designed to facilitate the management and processing of knowledge shards. Its primary purpose is to provide a suite of utility functions that enable efficient handling of data, logging, and domain inference, all of which are essential for the operation of Savant's knowledge management system. This document serves as an exhaustive guide to the module, detailing its architecture, functionality, integration points, and design philosophy.

## Core Purpose

At its core, `shard_tools.py` is dedicated to the manipulation and analysis of knowledge data. It provides functionalities such as hashing, JSON file operations, domain inference from text, and logging events related to knowledge processing. By encapsulating these utilities, `shard_tools.py` enhances the overall efficiency and clarity of the Savant ecosystem, allowing other modules to leverage its capabilities without reinventing the wheel.

## Detailed Analysis of Classes and Functions

### Constants and Directory Setup

```python
BASE = pathlib.Path(os.path.expanduser("~/savant"))
KDIR = BASE / "knowledge"
LOGS = BASE / "logs"

KDIR.mkdir(parents=True, exist_ok=True)
LOGS.mkdir(parents=True, exist_ok=True)
```

- **BASE**: This constant defines the base directory for the Savant application, ensuring that all knowledge and logs are stored in a user-specific directory.
- **KDIR** and **LOGS**: These constants define paths for knowledge and log storage, respectively. The directories are created if they do not already exist, ensuring that the application can operate smoothly without manual setup.

### Functions

#### `iso()`

```python
def iso() -> str:
    """Return the current time in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat()
```

- **Purpose**: To provide a standardized timestamp in ISO 8601 format, which is crucial for logging and event tracking.
- **Return Type**: Returns the current UTC time as a string.

#### `sha1_bytes(b: bytes)`

```python
def sha1_bytes(b: bytes) -> str:
    """Return the SHA-1 hash of the given bytes as a hexadecimal string."""
    h = hashlib.sha1()
    h.update(b)
    return h.hexdigest()
```

- **Purpose**: To compute the SHA-1 hash of a given byte input, which is useful for data integrity checks.
- **Input**: A byte object.
- **Return Type**: Returns the SHA-1 hash as a hexadecimal string.

#### `sha1_str(s: str)`

```python
def sha1_str(s: str) -> str:
    """Return the SHA-1 hash of the given string as a hexadecimal string."""
    return sha1_bytes(s.encode("utf-8", "ignore"))
```

- **Purpose**: To compute the SHA-1 hash of a string input, utilizing the `sha1_bytes` function for processing.
- **Input**: A string.
- **Return Type**: Returns the SHA-1 hash as a hexadecimal string.

#### `write_jsonl(path: pathlib.Path, rows: Iterable[Dict])`

```python
def write_jsonl(path: pathlib.Path, rows: Iterable[Dict]):
    """Append rows of dictionaries to a JSON Lines file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
```

- **Purpose**: To append rows of dictionaries to a JSON Lines file format, which is efficient for streaming data.
- **Input**: A `pathlib.Path` object and an iterable of dictionaries.
- **Behavior**: Ensures the directory exists before writing, and appends each dictionary as a new line in the file.

#### `save_json(path: pathlib.Path, obj: Dict)`

```python
def save_json(path: pathlib.Path, obj: Dict):
    """Save a dictionary as a JSON file with pretty printing."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
```

- **Purpose**: To save a dictionary as a formatted JSON file, enhancing readability.
- **Input**: A `pathlib.Path` object and a dictionary.
- **Behavior**: Creates the necessary directory structure and writes the JSON representation of the dictionary with indentation.

#### `infer_domains(text: str) -> List[str]`

```python
def infer_domains(text: str) -> List[str]:
    """Infer domains from the provided text based on keyword patterns."""
    text_lower = text.lower()
    hits = []
    for name, patterns in DOMAIN_MAP:
        if any(re.search(pattern, text_lower) for pattern in patterns):
            hits.append(name)
    return hits or ["general"]
```

- **Purpose**: To infer relevant domains from a given text using predefined keyword patterns.
- **Input**: A string of text.
- **Return Type**: A list of domain names or a default value of `["general"]` if no matches are found.
- **Behavior**: The function scans the text for keywords associated with specific domains, enhancing the contextual understanding of the content.

#### `tokenize_est(text: str) -> List[str]`

```python
def tokenize_est(text: str) -> List[str]:
    """Tokenize the input text into words and punctuation."""
    return re.findall(r"\w+|\S", text)
```

- **Purpose**: To tokenize the input text into individual words and punctuation marks.
- **Input**: A string of text.
- **Return Type**: A list of tokens extracted from the text.

#### `chunk_text(text: str, target_tokens=900, overlap_tokens=120) -> List[str]`

```python
def chunk_text(text: str, target_tokens=900, overlap_tokens=120) -> List[str]:
    """Chunk the input text into smaller segments based on token count."""
    tokens = tokenize_est(text)
    if not tokens:
        return []
    
    chunks = []
    i = 0
    while i < len(tokens):
        j = min(i + target_tokens, len(tokens))
        chunk = " ".join(tokens[i:j])
        chunks.append(chunk)
        if j == len(tokens):
            break
        i = max(0, j - overlap_tokens)
        if i == j: 
            i += 1
    return chunks
```

- **Purpose**: To divide a long text into smaller, manageable chunks based on a specified number of tokens, facilitating easier processing and analysis.
- **Input**: A string of text, with optional parameters for target and overlap token counts.
- **Return Type**: A list of text chunks.
- **Behavior**: It ensures that chunks overlap slightly for continuity, which is particularly useful in natural language processing tasks.

#### `level_from_shards(n: int) -> int`

```python
def level_from_shards(n: int) -> int:
    """Determine the level based on the number of shards."""
    thresholds = [(12000, 6), (7000, 5), (3000, 4), (1000, 3), (100, 2), (10, 1)]
    for threshold, level in thresholds:
        if n >= threshold:
            return level
    return 0
```

- **Purpose**: To assess the "level" of knowledge based on the number of shards, which can be useful for categorization and prioritization.
- **Input**: An integer representing the number of shards.
- **Return Type**: An integer indicating the level.
- **Behavior**: It uses predefined thresholds to categorize the shards into levels, facilitating a structured approach to knowledge management.

#### `log_event(kind: str, payload: Dict)`

```python
def log_event(kind: str, payload: Dict):
    """Log an event with a specific type and payload."""
    row = {"time": iso(), "type": kind, "payload": payload}
    with (LOGS / "knowledge_cluster.log").open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
```

- **Purpose**: To log events that occur within the knowledge processing workflow, enabling traceability and debugging.
- **Input**: A string representing the event type and a dictionary containing the event payload.
- **Behavior**: It appends the event to a log file, ensuring that the log is structured for easy parsing.

## Error Handling Patterns and Architectural Decisions

The architectural decisions within `shard_tools.py` prioritize clarity and robustness. The module employs a few key error-handling patterns:

1. **Directory Creation**: The use of `mkdir(parents=True, exist_ok=True)` ensures that the necessary directories are created without raising exceptions if they already exist. This promotes a seamless user experience.
  
2. **Graceful Handling of Empty Inputs**: Functions like `chunk_text` and `infer_domains` are designed to handle empty or non-matching inputs gracefully, returning sensible defaults (e.g., an empty list or a general domain).

3. **Logging**: The `log_event` function captures significant events, which aids in debugging and monitoring the application's behavior. By logging errors and events, the module provides insights into its operation, which is invaluable during development and production.

4. **Type Annotations**: The use of type annotations throughout the module enhances code clarity and assists in static type checking, which can prevent runtime errors.

## Integration Points with Other Savant Modules

`shard_tools.py` is designed to be modular and easily integrated with other components of the Savant ecosystem. Its utility functions can be invoked by various modules that require knowledge processing, logging, or domain inference capabilities. Key integration points include:

- **Knowledge Management**: Other modules that handle knowledge storage and retrieval can utilize the JSON writing and reading functions to manage data efficiently.
- **Event Tracking**: Modules that perform significant actions (e.g., data processing or user interactions) can log events using the `log_event` function, creating a comprehensive audit trail.
- **Natural Language Processing**: The text processing functions (e.g., `chunk_text`, `tokenize_est`, and `infer_domains`) can be leveraged by modules focused on NLP tasks, enhancing their ability to analyze and categorize content.

## Historical Rationale and Design Philosophy

The design philosophy behind `shard_tools.py` is rooted in the principles of clarity, efficiency, and modularity. The module was developed in response to the growing need for a structured approach to knowledge management within the Savant ecosystem. As the complexity of data handling increased, it became apparent that a dedicated set of tools was necessary to streamline operations.

Historically, the Savant project has emphasized the importance of clear documentation and user-friendly interfaces. This module adheres to those values by providing well-documented functions with intuitive names and behaviors. The use of Python's standard libraries (e.g., `json`, `hashlib`, `pathlib`) ensures that the code remains accessible and maintainable.

In summary, `shard_tools.py` stands as a testament to the Savant ecosystem's commitment to clarity and precision. Its well-defined functions and thoughtful design choices empower developers and users alike, fostering a robust environment for knowledge management and processing. As the Savant project continues to evolve, `shard_tools.py` will remain a cornerstone, supporting the intricate tapestry of knowledge that defines the ecosystem.