# README for `knowledge_synthesis_cluster.py`

## Overview

The `knowledge_synthesis_cluster.py` module is a pivotal component within the Savant ecosystem, designed to facilitate the synthesis of knowledge from raw text files. By reading, processing, and organizing textual data into structured shards, this module enhances the ability of Savant to manage and utilize information effectively. The overarching goal is to create a repository of knowledge that is both accessible and analyzable, thus enabling advanced insights and applications.

### Core Purpose

The core purpose of `knowledge_synthesis_cluster.py` is to automate the process of transforming unstructured text data into structured, domain-tagged shards. This process involves several key steps:

1. **Reading Raw Texts**: The module reads normalized text files from a specified directory.
2. **Text Chunking**: It splits the text into overlapping chunks to ensure comprehensive coverage of the content.
3. **Deduplication**: Each chunk is hashed to prevent duplicate entries, ensuring that only unique content is stored.
4. **Storage**: The processed shards are saved in a structured format, organized by domain and content hash.
5. **Summary Generation**: A synthesis summary is generated, providing insights into the synthesis process, including the number of texts processed and shards created.

## Detailed Analysis of Classes and Functions

The module is structured around several key functions, each serving a specific role in the knowledge synthesis process.

### Constants and Paths

```python
BASE = pathlib.Path(os.path.expanduser("~/savant"))
KDIR = BASE / "knowledge"
RAW  = KDIR / "raw_text"
SHRD = KDIR / "shards"
META = KDIR / "meta"
LOGS = BASE / "logs"
```

These constants define the base directory for the Savant application and the subdirectories for raw text, shards, metadata, and logs. The use of `pathlib` ensures cross-platform compatibility for file paths.

### Directory Creation

```python
for p in [KDIR, RAW, SHRD, META, LOGS]: p.mkdir(parents=True, exist_ok=True)
```

This loop ensures that all necessary directories exist, creating them if they do not. This proactive approach prevents runtime errors related to missing directories.

### Function: `iso()`

```python
def iso(): return datetime.now(timezone.utc).isoformat()
```

The `iso` function returns the current date and time in ISO 8601 format. This is used throughout the module for timestamping events and records, ensuring a consistent format for logging and metadata.

### Function: `synth_one_text(fp: pathlib.Path, shards_added: List[str])`

```python
def synth_one_text(fp: pathlib.Path, shards_added: List[str]):
    text = fp.read_text(encoding="utf-8", errors="ignore")
    text = text.strip()
    if not text: return 0
    doms = infer_domains(text)
    chunks = chunk_text(text, target_tokens=900, overlap_tokens=120)
    added = 0
    for ch in chunks:
        body = ch.strip()
        if not body: continue
        hid = sha1_str(body)
        domains = doms or ["general"]
        for d in domains:
            out = SHRD / d
            out.mkdir(parents=True, exist_ok=True)
            path = out / f"{hid}.json"
            if path.exists(): 
                continue
            doc = {
                "id": hid,
                "domain": d,
                "source": str(fp),
                "created": iso(),
                "tokens_est": len(body.split()),
                "body": body
            }
            save_json(path, doc)
            shards_added.append(str(path))
            added += 1
    return added
```

The `synth_one_text` function is responsible for processing a single text file. It performs the following tasks:

1. **Reading the Text**: The text is read from the specified file path, with error handling for encoding issues.
2. **Domain Inference**: The function infers the domains associated with the text using the `infer_domains` function.
3. **Chunking**: The text is divided into overlapping chunks using the `chunk_text` function, which allows for better context retention.
4. **Deduplication**: Each chunk is hashed using `sha1_str` to create a unique identifier.
5. **Storage**: For each domain associated with the chunk, a directory is created (if it does not already exist), and the chunk is saved as a JSON file.
6. **Tracking Added Shards**: The paths of added shards are recorded for summary generation.

The function returns the total number of shards added, allowing for feedback on the processing of the text.

### Function: `main()`

```python
def main():
    files = sorted(RAW.glob("*.txt"))
    if not files:
        footer("Error.", "error")
        return
    print(f"🧪 Synthesizing from {len(files)} texts...")
    shards_added: List[str] = []
    total = 0
    for i, fp in enumerate(files, 1):
        added = synth_one_text(fp, shards_added)
        total += added
        if added:
            print(f"   • {fp.name}: +{added} shards")
    current_count = sum(1 for _ in SHRD.rglob("*.json"))
    level = level_from_shards(current_count)
    summary = {
        "time": iso(),
        "texts": len(files),
        "added": total,
        "shard_total": current_count,
        "level": level
    }
    (META / "synthesis_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    log_event("knowledge_synthesis_complete", summary)
    footer("Complete.", "done")
```

The `main` function orchestrates the entire synthesis process:

1. **File Discovery**: It retrieves all text files from the raw text directory and sorts them.
2. **Error Handling**: If no files are found, it logs an error and exits gracefully.
3. **Processing Loop**: For each file, it calls `synth_one_text` to process the text and track the total shards added.
4. **Level Calculation**: After processing, it calculates the current level based on the total number of shards using `level_from_shards`.
5. **Summary Generation**: A summary of the synthesis process is created and saved as a JSON file in the metadata directory.
6. **Logging**: The completion of the synthesis process is logged for future reference.

### Error-Handling Patterns

The module employs several error-handling strategies to ensure robustness:

- **File Reading**: When reading text files, the `errors="ignore"` parameter is used to gracefully handle any encoding issues without crashing.
- **Empty Text Check**: After reading a file, the module checks if the text is empty and returns early if so, preventing unnecessary processing.
- **Directory Creation**: The use of `mkdir(parents=True, exist_ok=True)` ensures that the module does not fail if the directory structure is not present.
- **File Existence Check**: Before writing a shard, the module checks if a file with the same hash already exists, preventing duplicate entries.

### Architectural Decisions

The design of `knowledge_synthesis_cluster.py` reflects a commitment to modularity and clarity. The separation of concerns is evident in the distinct functions that handle specific tasks, allowing for easier maintenance and testing. The use of type hints enhances readability and provides clarity on expected input and output types.

The choice of JSON for storing shards is intentional, as it allows for easy serialization and deserialization of structured data. This format is widely supported and facilitates integration with other systems and modules within the Savant ecosystem.

## Integration Points with Other Savant Modules

The `knowledge_synthesis_cluster.py` module integrates seamlessly with other components of the Savant ecosystem:

- **Shard Tools**: Functions like `chunk_text`, `infer_domains`, and `sha1_str` are imported from the `shard_tools` module, highlighting a collaborative architecture where shared utilities are leveraged across multiple modules.
- **Logging and Metadata**: The module logs events using `log_event`, which can be utilized by other modules for monitoring and analytics. The synthesis summary is saved in the metadata directory, allowing other components to access and utilize this information.
- **Domain Inference**: The inferred domains can be used by other modules for categorization, search, and retrieval tasks, enhancing the overall functionality of the Savant system.

## Historical Rationale and Design Philosophy

The `knowledge_synthesis_cluster.py` module has evolved in response to the growing need for efficient knowledge management in an increasingly data-driven world. As the volume of text data expands, the necessity for automated processing and synthesis becomes paramount. This module was designed to address these challenges by providing a robust framework for knowledge extraction and organization.

The design philosophy emphasizes clarity, precision, and modularity. By adhering to the Savant Documentation Doctrine, the module aims to be self-explanatory and easy to navigate. The use of clear function names, type hints, and structured logging contributes to a maintainable codebase that can adapt to future requirements.

In conclusion, `knowledge_synthesis_cluster.py` serves as a cornerstone of the Savant ecosystem, enabling the transformation of raw text into valuable knowledge. Its thoughtful design and integration capabilities position it as a vital tool for researchers, developers, and data scientists alike, fostering a deeper understanding of the information landscape.