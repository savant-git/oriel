# README for `cleanup_engine.py`

## Overview

The `cleanup_engine.py` module is a critical component of the Savant ecosystem, responsible for managing and executing file cleanup operations. Its primary role is to ensure that files generated during data processing are appropriately managed, preventing clutter and maintaining system efficiency. This document provides a comprehensive overview of the module, detailing its structure, functionality, design philosophy, error handling mechanisms, relationships with other modules, and internal flow.

## Role within Savant’s Modular Ecosystem

Savant is designed as a modular system, where each component serves a specific purpose while interacting seamlessly with others. The `cleanup_engine.py` module fits into this architecture by:

1. **File Management**: It automates the process of identifying and removing unnecessary files, thereby optimizing storage and improving performance.
2. **Integration**: It interacts with other modules, such as data processing engines and logging systems, to ensure that cleanup operations are executed at appropriate times and under the right conditions.
3. **Configurability**: The module allows for configurable cleanup policies, enabling users to tailor file management strategies to their specific needs.

## Class and Function Overview

The `cleanup_engine.py` module is structured around several key classes and functions, each serving a distinct purpose. Below is a detailed description of each.

### Classes

#### 1. `CleanupEngine`

**Purpose**: The `CleanupEngine` class is the core of the cleanup functionality. It orchestrates the file cleanup process by managing the lifecycle of cleanup operations.

- **Attributes**:
  - `cleanup_policy`: An instance of `CleanupPolicy`, defining the rules for file deletion.
  - `logger`: An instance of a logging class, used to log actions and errors during cleanup.
  
- **Methods**:
  - `__init__(self, cleanup_policy: CleanupPolicy, logger: Logger)`: Initializes the cleanup engine with a specified policy and logger.
  - `execute_cleanup(self)`: Executes the cleanup process based on the defined policy.
  - `log_cleanup_action(self, action: str)`: Logs the actions taken during cleanup for auditing and debugging purposes.

#### 2. `CleanupPolicy`

**Purpose**: The `CleanupPolicy` class encapsulates the rules and criteria for file cleanup operations.

- **Attributes**:
  - `file_age_limit`: Specifies the maximum age of files (in days) to be considered for deletion.
  - `file_size_limit`: Specifies the maximum size (in MB) for files to be retained.
  
- **Methods**:
  - `is_file_stale(self, file: File) -> bool`: Determines if a given file exceeds the age limit.
  - `is_file_large(self, file: File) -> bool`: Determines if a given file exceeds the size limit.

### Functions

#### 1. `find_files_to_cleanup(directory: str, policy: CleanupPolicy) -> List[File]`

**Purpose**: This function scans a specified directory and returns a list of files that meet the criteria defined in the `CleanupPolicy`.

- **Parameters**:
  - `directory`: The path to the directory to be scanned.
  - `policy`: An instance of `CleanupPolicy` used to filter files.
  
- **Returns**: A list of files eligible for cleanup.

#### 2. `remove_file(file: File) -> None`

**Purpose**: This function deletes a specified file from the filesystem.

- **Parameters**:
  - `file`: The file object to be deleted.
  
- **Returns**: None.

## Design Philosophy

The design of `cleanup_engine.py` adheres to several key principles:

1. **Modularity**: Each class and function has a single responsibility, promoting clarity and maintainability.
2. **Configurability**: Users can define their cleanup policies, allowing for flexibility in file management.
3. **Logging**: Comprehensive logging is integrated throughout the module to facilitate monitoring and debugging.
4. **Efficiency**: The module is designed to minimize resource usage during file operations, ensuring that cleanup processes do not adversely affect system performance.

## Error Handling

Error handling is a critical aspect of the `cleanup_engine.py` module. The following strategies are employed:

1. **Try-Except Blocks**: Key operations, such as file deletion and directory scanning, are wrapped in try-except blocks to catch and handle exceptions gracefully.
   
   ```python
   try:
       remove_file(file)
   except OSError as e:
       self.logger.error(f"Failed to remove file {file.name}: {e}")
   ```

2. **Custom Exceptions**: Specific exceptions can be raised for anticipated errors, such as `FileNotFoundError`, to provide more context to the user.
   
3. **Logging Errors**: All errors are logged using the logger instance, ensuring that issues can be tracked and resolved efficiently.

## Relationships to Other Modules

The `cleanup_engine.py` module interacts with several other components within the Savant ecosystem:

1. **Logger Module**: The logging functionality is crucial for tracking cleanup operations and errors. The `logger` instance is passed to the `CleanupEngine` class to facilitate this.
  
2. **File Management Module**: The cleanup engine relies on file management utilities to perform operations like file listing and deletion.

3. **Configuration Module**: The `CleanupPolicy` can be configured through the Savant configuration module, allowing users to set their cleanup preferences.

4. **Data Processing Modules**: The cleanup engine may be triggered after data processing tasks to ensure that temporary files are cleared promptly.

## Internal Flow

The internal flow of the `cleanup_engine.py` module can be summarized in the following steps:

1. **Initialization**: An instance of `CleanupEngine` is created, initialized with a `CleanupPolicy` and a `Logger`.
   
   ```python
   cleanup_policy = CleanupPolicy(file_age_limit=30, file_size_limit=10)
   logger = Logger()
   cleanup_engine = CleanupEngine(cleanup_policy, logger)
   ```

2. **Execution of Cleanup**: The `execute_cleanup` method is called, which initiates the cleanup process.

   ```python
   cleanup_engine.execute_cleanup()
   ```

3. **File Discovery**: The `find_files_to_cleanup` function is invoked to retrieve a list of files that meet the cleanup criteria.

   ```python
   files_to_cleanup = find_files_to_cleanup("/path/to/directory", cleanup_policy)
   ```

4. **File Deletion**: For each file identified, the `remove_file` function is called to delete it. Errors during deletion are handled and logged.

   ```python
   for file in files_to_cleanup:
       try:
           remove_file(file)
           cleanup_engine.log_cleanup_action(f"Removed file: {file.name}")
       except OSError as e:
           cleanup_engine.logger.error(f"Failed to remove file {file.name}: {e}")
   ```

5. **Completion**: Upon completion, the cleanup process logs a summary of actions taken, providing visibility into the operations performed.

## Conclusion

The `cleanup_engine.py` module is a vital part of the Savant ecosystem, ensuring efficient file management through automated cleanup processes. Its design emphasizes modularity, configurability, and robust error handling, making it a reliable tool for maintaining system performance. By adhering to the principles outlined in this document, the module contributes significantly to the overall functionality and efficiency of Savant. 

For further information or to contribute to the development of the `cleanup_engine.py` module, please refer to the Savant documentation or contact the development team.