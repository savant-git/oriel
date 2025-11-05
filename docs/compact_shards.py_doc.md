# README for `compact_shards.py`

## Overview

The `compact_shards.py` module is an integral component of the Savant ecosystem, designed to manage and optimize the storage of historical versioned shard files. Its primary function is to identify, archive, or delete older versions of these files according to user-defined parameters, thereby maintaining an organized and efficient file structure. This document provides a comprehensive overview of the module, detailing its purpose, architecture, error-handling strategies, integration points, and the historical rationale behind its design.

## Core Purpose

The core purpose of `compact_shards.py` is to facilitate the management of versioned Python scripts within the Savant framework. By compacting these files, the module helps prevent clutter and ensures that only the most relevant versions of scripts are retained. This is particularly important in environments where multiple iterations of scripts are generated over time, as it allows for easy access to the latest versions while safeguarding older iterations in a designated archive.

### Key Features

- **Archiving and Deletion**: The module provides options to either archive older versions of scripts into a trash directory or permanently delete them.
- **Retention Policy**: Users can specify how many of the most recent versions to keep for each script stem, allowing for tailored version control.
- **Dry Run Mode**: A dry run option allows users to preview the actions that would be taken without making any actual changes, enhancing safety and user confidence.
- **Logging**: The module logs its operations, providing a transparent record of actions taken for future reference.

## Detailed Analysis of Classes and Functions

The `compact_shards.py` module consists of several key functions, each serving a specific role in the overall operation of the script. Below is a detailed breakdown of each function:

### 1. `parse_variant(file: Path)`

This function is responsible for parsing the filename of a versioned shard to extract its components: the stem, sequence number, and date.

- **Parameters**: 
  - `file`: A `Path` object representing the file to be parsed.
  
- **Returns**: 
  - A tuple containing the stem and a sortable key (year, month, day, sequence number, and modification time) if the filename matches the expected pattern; otherwise, it returns `None`.

- **Error Handling**: 
  - If the filename does not match the expected pattern, it returns `None`.
  - In case of a parsing error, it falls back to using the file's modification time.

### 2. `list_variants(root: Path)`

This function scans the specified directory for versioned shard files and groups them by their stems.

- **Parameters**: 
  - `root`: A `Path` object indicating the root directory to search.
  
- **Returns**: 
  - A dictionary where keys are stems and values are lists of tuples containing the file paths and their corresponding sort keys.

### 3. `ensure_trash()`

This function ensures that a trash directory exists for archiving old files.

- **Returns**: 
  - A `Path` object representing the newly created trash directory.

- **Error Handling**: 
  - It uses `mkdir` with `parents=True` to create the directory structure if it does not exist, ensuring no exceptions are raised if the directory already exists.

### 4. `log_event(kind, payload)`

This function logs events to a JSON Lines file for audit purposes.

- **Parameters**: 
  - `kind`: A string indicating the type of event (e.g., "compact_complete").
  - `payload`: A dictionary containing additional data related to the event.

- **Error Handling**: 
  - It handles file writing errors gracefully, ensuring that logging does not disrupt the main functionality of the script.

### 5. `main()`

The main function orchestrates the execution of the script, handling user input and invoking the necessary functions to perform the compacting operation.

- **Functionality**:
  - It sets up command-line argument parsing using `argparse`.
  - It validates the root directory and collects versioned files.
  - It determines which files to remove based on the user-defined retention policy.
  - It performs the archiving or deletion of files as specified by the user.

- **Error Handling**: 
  - It checks for the existence of the root directory and exits with an error message if not found.
  - It catches exceptions during file operations (deletion or moving) and logs the errors without terminating the entire process.

## Architectural Decisions

The architecture of `compact_shards.py` is designed with clarity and maintainability in mind. Key architectural decisions include:

- **Modular Design**: Each function is focused on a single responsibility, making the code easier to understand, test, and maintain.
- **Use of Pathlib**: The module employs `pathlib` for file path manipulations, enhancing cross-platform compatibility and readability.
- **Logging Mechanism**: The logging of events provides a robust audit trail, allowing for easy troubleshooting and monitoring of the module's operations.
- **Command-Line Interface**: The use of `argparse` for command-line argument parsing facilitates user interaction and enhances the module's usability.

## Integration Points with Other Savant Modules

`compact_shards.py` integrates seamlessly with other components of the Savant ecosystem. Its primary interactions include:

- **File Management**: The module operates on files generated by other Savant services, ensuring that versioned scripts are managed effectively.
- **Logging Framework**: It utilizes the existing logging infrastructure within Savant, allowing for consistent logging practices across modules.
- **User Interface**: The command-line interface can be invoked from other scripts or services, enabling automated workflows that include file compaction as part of larger processes.

## Historical Rationale and Design Philosophy

The development of `compact_shards.py` was driven by the need for efficient management of versioned files within the Savant ecosystem. As the number of scripts and their versions grew, it became increasingly important to implement a systematic approach to file organization. 

The design philosophy behind this module emphasizes:

- **Clarity First**: The module adheres to the Savant Documentation Doctrine, prioritizing clear and understandable code that is well-documented.
- **Precision Always**: Every function is crafted to perform its task accurately, minimizing the risk of errors and ensuring reliability.
- **User Empowerment**: By providing options for archiving, deletion, and dry runs, the module empowers users to make informed decisions about their file management practices.

## Conclusion

In summary, `compact_shards.py` is a vital tool within the Savant ecosystem, designed to manage versioned shard files efficiently. Its modular architecture, robust error handling, and integration capabilities make it a reliable choice for users seeking to maintain an organized and effective file structure. By adhering to principles of clarity and precision, the module not only meets the immediate needs of file management but also aligns with the broader goals of the Savant framework, fostering an environment of efficiency and reliability.