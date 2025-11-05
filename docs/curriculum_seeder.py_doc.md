# README for `curriculum_seeder.py`

## Introduction

The `curriculum_seeder.py` module serves as a vital component within the Savant ecosystem, designed to automate the process of gathering educational resources from various online platforms. Its primary function is to read URLs from specified seed files, fetch the content from these URLs, and then store the fetched data in a structured format for further processing and analysis. The module adheres to the principles of clarity and precision, ensuring that users can easily understand its functionality and integrate it within their workflows.

## Core Purpose

The core purpose of the `curriculum_seeder.py` module is to facilitate the ingestion of educational content from the web into the Savant knowledge base. This is achieved through a systematic approach that includes:

- **Reading Seeds**: The module reads seed URLs from text files located in the `~/savant/knowledge/seeds/` directory.
- **Content Fetching**: It fetches content from the specified URLs while respecting the `robots.txt` directives of the websites.
- **Content Deduplication**: The module ensures that duplicate content is not ingested by utilizing a combination of URL and content hashing.
- **Content Extraction**: It extracts text from various content types, including HTML, PDF, and plain text formats.
- **Parallel Processing**: The module supports parallel processing to enhance performance and efficiency during content fetching.
- **Rate Limiting**: It implements rate limiting to prevent overwhelming the target servers with requests.
- **Structured Output**: The fetched content is saved in a structured format, including original files, normalized text, and metadata for each entry.

## Detailed Analysis of Classes and Functions

The `curriculum_seeder.py` module is structured around several key functions that encapsulate its functionality. Below is a detailed analysis of each function.

### 1. `rate_limit(url: str)`

This function implements a trivial per-host rate limiter to control the frequency of requests sent to the same host. It ensures that requests are spaced out by a defined interval (`RATE_LIMIT_PER_HOST`).

**Parameters**:
- `url`: The URL being fetched.

### 2. `iso() -> str`

This utility function returns the current timestamp in ISO 8601 format. It is used to timestamp metadata entries.

### 3. `sha1(b: bytes) -> str`

This function computes the SHA-1 hash of the given byte input. It is primarily used to generate unique identifiers for content based on its binary data.

**Parameters**:
- `b`: The byte content to hash.

### 4. `load_robots(base_url: str) -> RobotFileParser`

This function loads the `robots.txt` file for a given base URL and returns a `RobotFileParser` object. This parser is used to determine whether the module is allowed to fetch content from the specified URL.

**Parameters**:
- `base_url`: The base URL from which to load the `robots.txt`.

### 5. `allowed_by_robots(url: str, agent="savant-seeder") -> bool`

This function checks if the specified URL can be fetched according to the `robots.txt` rules. If the rules are not accessible or an error occurs, it defaults to allowing access.

**Parameters**:
- `url`: The URL to check.
- `agent`: The user-agent string to use for the check.

### 6. `html_to_text(content: bytes) -> str`

This function converts HTML content into plain text by removing non-text elements (like scripts and styles) and collapsing excessive whitespace.

**Parameters**:
- `content`: The HTML content to process.

### 7. `pdf_to_text(content: bytes) -> str`

This function extracts text from PDF files using the `pdfminer` library. It returns an empty string if an error occurs during extraction.

**Parameters**:
- `content`: The PDF content to process.

### 8. `normalize_text_by_type(ct: str, content: bytes, url: str) -> str`

This function normalizes text based on its content type. It determines the appropriate method for extracting text based on the content type or file extension.

**Parameters**:
- `ct`: The content type of the fetched resource.
- `content`: The raw bytes of the resource.
- `url`: The URL of the resource.

### 9. `fetch_one(url: str) -> Tuple[str, Dict]`

This is a core function that fetches content from a single URL, processes it, and returns the path to the normalized text along with metadata about the fetch operation.

**Parameters**:
- `url`: The URL to fetch.

**Returns**:
- A tuple containing the path to the raw text file and a dictionary with metadata.

### 10. `load_seeds() -> List[str]`

This function loads seed URLs from text files located in the `~/savant/knowledge/seeds/` directory. It returns a sorted list of unique URLs.

### 11. `main()`

The main entry point of the module. It orchestrates the process of loading seeds, fetching content, and writing metadata to a log file. It also provides user feedback on the status of each fetch operation.

## Error-Handling Patterns and Architectural Decisions

The `curriculum_seeder.py` module employs several error-handling patterns to ensure robustness and reliability:

- **Try-Except Blocks**: Many functions, such as `fetch_one`, utilize try-except blocks to catch exceptions that may arise during network operations, file I/O, or content processing. This allows the module to gracefully handle errors and continue processing other URLs.
  
- **Metadata Logging**: Each fetch operation generates metadata that includes status and reason for any failures. This metadata is logged in a structured format (`ingest.jsonl`), allowing for easy post-processing and debugging.

- **Graceful Degradation**: Functions like `pdf_to_text` return an empty string instead of raising an error if text extraction fails, allowing the process to continue without interruption.

- **Rate Limiting**: The implementation of a rate limiter helps prevent the module from overwhelming target servers, reducing the likelihood of being blocked or throttled.

## Integration Points with Other Savant Modules

The `curriculum_seeder.py` module is designed to integrate seamlessly with other components of the Savant ecosystem. Key integration points include:

- **Knowledge Base**: The module directly interacts with the Savant knowledge base by saving fetched content and metadata in structured directories (`knowledge/source/`, `knowledge/raw_text/`, and `knowledge/meta/`).

- **Logging and Monitoring**: The module writes logs that can be consumed by other Savant modules for monitoring and analysis purposes.

- **User Interface**: The module’s output can be utilized by user-facing components of the Savant ecosystem, such as dashboards or reporting tools, to present ingested content to end-users.

## Historical Rationale and Design Philosophy

The design of the `curriculum_seeder.py` module is rooted in the historical context of educational resource aggregation and the need for structured knowledge management. As the internet has become a vast repository of information, the challenge of curating and organizing this content has grown increasingly complex. The following principles guided the development of this module:

- **User-Centric Design**: The module is designed with the end-user in mind, providing clear feedback and structured outputs that facilitate ease of use and integration.

- **Modularity and Reusability**: Functions are modular, allowing for easy reuse and adaptation in other contexts within the Savant ecosystem. This modularity enhances maintainability and scalability.

- **Adherence to Standards**: The module follows established coding standards and documentation practices, ensuring clarity and ease of understanding for developers and users alike.

- **Focus on Performance**: By implementing parallel processing and rate limiting, the module is optimized for performance, capable of handling large volumes of requests without compromising on reliability.

## Conclusion

The `curriculum_seeder.py` module is a cornerstone of the Savant ecosystem, enabling the efficient ingestion of educational resources from the web. Through its robust architecture, thoughtful error handling, and seamless integration with other components, it exemplifies the principles of clarity, precision, and user-centric design. As the landscape of online education continues to evolve, this module stands ready to adapt and grow, ensuring that Savant remains at the forefront of knowledge management and resource aggregation.