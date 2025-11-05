# README for `version_engine.py`

## Overview

The `version_engine.py` module is a pivotal component of the Savant ecosystem, designed to manage and manipulate versioning information across various entities within the system. This module facilitates the tracking of software versions, ensuring that all components are aligned and compatible, which is critical for maintaining system integrity and facilitating updates. 

## Role within Savant’s Modular Ecosystem

In the Savant architecture, modularity is key. Each module serves a specific purpose while interacting seamlessly with others. The `version_engine.py` module serves as the authoritative source for version control, providing functionality for:

- **Version Comparison**: Determining the relationship between different versions (e.g., whether one version is newer than another).
- **Version Parsing**: Extracting version information from strings and validating their formats.
- **Version Management**: Facilitating the incrementing of version numbers and managing version histories.

By centralizing version control, `version_engine.py` ensures that all modules can reference a consistent versioning scheme, which is essential for dependency management and compatibility checks.

## Class and Function Descriptions

### Classes

#### `Version`

The `Version` class encapsulates the concept of a software version. It provides methods for parsing, comparing, and manipulating version strings.

##### Attributes
- `major`: An integer representing the major version number.
- `minor`: An integer representing the minor version number.
- `patch`: An integer representing the patch version number.
- `pre_release`: A string representing pre-release identifiers (if any).
- `build`: A string representing build metadata (if any).

##### Methods
- `__init__(self, version_string: str)`: Initializes a `Version` object by parsing the provided version string. Raises `ValueError` if the format is invalid.
- `__str__(self)`: Returns a string representation of the version in the format "major.minor.patch".
- `__lt__(self, other: 'Version')`: Compares this version with another version for less-than.
- `__eq__(self, other: 'Version')`: Compares this version with another version for equality.
- `increment_major(self)`: Increments the major version number and resets minor and patch to zero.
- `increment_minor(self)`: Increments the minor version number and resets patch to zero.
- `increment_patch(self)`: Increments the patch version number.

#### `VersionManager`

The `VersionManager` class provides higher-level functionality for managing multiple versions, including tracking the current version and maintaining a history of changes.

##### Attributes
- `current_version`: An instance of `Version` representing the current version.
- `version_history`: A list of `Version` instances representing the history of versions.

##### Methods
- `__init__(self, initial_version_string: str)`: Initializes the `VersionManager` with the given initial version string.
- `update_version(self, new_version_string: str)`: Updates the current version to a new version, adding the previous version to the history.
- `get_version_history(self)`: Returns the history of versions as a list of strings.
- `is_newer(self, other_version_string: str)`: Checks if the current version is newer than the provided version string.

### Functions

#### `parse_version(version_string: str) -> Version`

This function takes a version string as input and returns an instance of the `Version` class. It raises `ValueError` if the input string does not conform to the expected versioning format.

#### `compare_versions(version_string_a: str, version_string_b: str) -> int`

This function compares two version strings and returns:
- `-1` if `version_string_a` is older,
- `0` if they are equal,
- `1` if `version_string_a` is newer.

It utilizes the `Version` class for parsing and comparison.

## Design Philosophy

The design philosophy of `version_engine.py` is grounded in clarity, modularity, and extensibility. The module is structured to allow for easy integration and interaction with other components of the Savant system. Key principles include:

- **Single Responsibility**: Each class and function has a clear, defined purpose. The `Version` class focuses on version representation and comparison, while the `VersionManager` handles version history and updates.
- **Encapsulation**: Internal details of version parsing and comparison are encapsulated within the `Version` class, providing a clean interface for external interaction.
- **Error Handling**: Robust error handling is implemented to ensure that invalid version strings are caught early, preventing cascading failures in the system.

## Error Handling

Error handling in `version_engine.py` is critical to maintaining system stability. The following strategies are employed:

- **Input Validation**: The `Version` class constructor validates the format of the version string. If the string does not match the expected pattern (e.g., "X.Y.Z"), a `ValueError` is raised.
  
  ```python
  if not re.match(r'^\d+\.\d+\.\d+(-[a-zA-Z0-9]+(\.[a-zA-Z0-9]+)*)?(\+[a-zA-Z0-9]+(\.[a-zA-Z0-9]+)*)?$', version_string):
      raise ValueError(f"Invalid version string: {version_string}")
  ```

- **Type Checking**: Functions that accept version strings ensure that the input is of the correct type and format before proceeding with operations. This prevents type-related errors during comparisons.

- **Graceful Failures**: Instead of allowing the application to crash, the module raises exceptions that can be caught and handled at higher levels in the application, allowing for graceful degradation of functionality.

## Relationships to Other Modules

The `version_engine.py` module interacts with several other components within the Savant ecosystem:

- **Dependency Management**: Other modules that rely on specific versions of components can utilize the `VersionManager` to check compatibility and manage updates.
- **Configuration Management**: The module may interact with configuration files that specify version constraints, ensuring that the system adheres to defined versioning policies.
- **Update Mechanisms**: When new versions of components are released, the `version_engine.py` module can be used to facilitate the update process, ensuring that dependencies are correctly resolved.

## Internal Flow

The internal flow of `version_engine.py` can be summarized as follows:

1. **Initialization**: When a `Version` object is created, the constructor parses the provided version string. If the string is valid, the major, minor, patch, pre-release, and build attributes are set accordingly.

2. **Version Comparison**: When comparing versions, the `__lt__` and `__eq__` methods are invoked. These methods break down the version strings into their components and compare them in order of significance (major, minor, patch).

3. **Version Management**: The `VersionManager` maintains the current version and a history of previous versions. When updating the version, the `update_version` method is called, which creates a new `Version` object for the new version string, adds the current version to the history, and updates the `current_version` attribute.

4. **External Interaction**: Other modules can interact with `version_engine.py` through its public interface. For instance, they can call `compare_versions` to determine version relationships or use `VersionManager` to manage their own versioning needs.

5. **Error Handling**: Throughout the process, any invalid inputs or operations trigger appropriate exceptions, which can be caught by the calling module to handle errors effectively.

## Conclusion

The `version_engine.py` module is a fundamental part of the Savant ecosystem, providing essential functionality for version management. Its clear design, robust error handling, and modular structure make it a reliable component for ensuring consistency and compatibility across the system. By adhering to the principles of encapsulation and single responsibility, it serves as a model for how other modules within Savant can be developed and integrated. 

This README serves as a comprehensive guide to understanding the `version_engine.py` module, ensuring that developers can effectively utilize its capabilities within the broader Savant framework.