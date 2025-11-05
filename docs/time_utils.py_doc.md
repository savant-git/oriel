# README for `time_utils.py`

## Overview

The `time_utils.py` module is a critical component of the Savant ecosystem, designed to provide a suite of utilities for handling temporal data. Within the modular architecture of Savant, this module serves as a foundational layer that simplifies time manipulation, formatting, and calculations. It is essential for ensuring that time-related operations are consistent, efficient, and accurate across the entire system.

## Role within Savant’s Modular Ecosystem

In Savant’s architecture, `time_utils.py` acts as a utility module that provides reusable functions and classes for time management. It is leveraged by various other modules, including data processing, event scheduling, and logging systems. The utility functions encapsulate common operations involving dates and times, ensuring that developers do not need to repeatedly implement the same logic, thereby promoting code reusability and maintainability.

## Classes and Functions

### Classes

#### 1. `TimeFormatter`

**Purpose**: The `TimeFormatter` class is responsible for converting time objects into human-readable string formats and vice versa. It provides a consistent interface for formatting and parsing time-related data.

- **Attributes**:
  - `format_string`: A string that defines the format in which time should be represented.

- **Methods**:
  - `__init__(self, format_string: str)`: Initializes the `TimeFormatter` with a specified format string.
  - `format_time(self, time_obj: datetime) -> str`: Converts a `datetime` object into a string based on the `format_string`.
  - `parse_time(self, time_string: str) -> datetime`: Converts a string representation of time back into a `datetime` object.

#### 2. `TimeCalculator`

**Purpose**: The `TimeCalculator` class provides methods for performing arithmetic operations on time objects, such as adding or subtracting time intervals.

- **Attributes**: None.

- **Methods**:
  - `add_time(self, start_time: datetime, delta: timedelta) -> datetime`: Returns a new `datetime` object that is the result of adding a `timedelta` to a `datetime`.
  - `subtract_time(self, start_time: datetime, delta: timedelta) -> datetime`: Returns a new `datetime` object that is the result of subtracting a `timedelta` from a `datetime`.
  - `time_difference(self, start_time: datetime, end_time: datetime) -> timedelta`: Calculates the difference between two `datetime` objects and returns it as a `timedelta`.

### Functions

#### 1. `get_current_time()`

**Purpose**: This function retrieves the current time in UTC.

- **Returns**: A `datetime` object representing the current UTC time.

#### 2. `convert_to_utc(local_time: datetime) -> datetime`

**Purpose**: Converts a local `datetime` object to UTC.

- **Parameters**: 
  - `local_time`: A `datetime` object representing local time.
  
- **Returns**: A `datetime` object in UTC.

#### 3. `is_time_valid(time_string: str, format_string: str) -> bool`

**Purpose**: Validates whether a given time string matches a specified format.

- **Parameters**:
  - `time_string`: A string representation of time.
  - `format_string`: The format against which to validate the time string.
  
- **Returns**: A boolean indicating whether the time string is valid.

## Design Philosophy

The design philosophy of `time_utils.py` is centered around simplicity, clarity, and reusability. Each class and function is designed to perform a single responsibility, adhering to the Single Responsibility Principle (SRP). This modular approach allows for easier testing, debugging, and extension.

The module leverages Python's built-in `datetime` and `timedelta` classes to ensure that all time-related operations are based on robust and well-tested constructs. The use of clear naming conventions and type hints enhances code readability and aids in development.

## Error Handling

Error handling in `time_utils.py` is implemented using Python's built-in exception handling mechanisms. The following practices are employed:

1. **Input Validation**: Functions such as `is_time_valid` perform checks to ensure that inputs conform to expected formats. Invalid inputs raise `ValueError` exceptions with descriptive messages.

2. **Type Checking**: Type hints are used throughout the module to indicate expected parameter types. Functions enforce type checks at runtime, raising `TypeError` when inputs do not match expected types.

3. **Graceful Degradation**: When errors occur, the module is designed to fail gracefully. For instance, if a time conversion fails, the function will return `None` or raise a specific exception rather than crashing the entire application.

## Relationships to Other Modules

`time_utils.py` interacts with several other modules within the Savant ecosystem:

- **Data Processing Modules**: These modules utilize `TimeFormatter` and `TimeCalculator` to preprocess time data before analysis. For example, time stamps from logs may be formatted for reporting.

- **Event Scheduling**: The scheduling module relies on `get_current_time` and `convert_to_utc` to manage event timings accurately, ensuring all events are recorded in a consistent time zone.

- **Logging**: The logging module uses `TimeFormatter` to timestamp log entries, providing clear and consistent time references for debugging and auditing purposes.

## Internal Flow

The internal flow of `time_utils.py` is structured to allow for seamless interaction between its components. Here’s a high-level overview of how the module operates:

1. **Initialization**: When a user instantiates a `TimeFormatter`, they provide a format string. This string is stored as an attribute for later use in formatting and parsing operations.

2. **Time Retrieval**: The `get_current_time` function can be called independently to fetch the current UTC time, which can then be formatted using `TimeFormatter`.

3. **Time Formatting**: The `format_time` method of `TimeFormatter` takes a `datetime` object and converts it to a string based on the user-defined format. This formatted string can be used for display or logging.

4. **Time Parsing**: Conversely, a time string can be parsed back into a `datetime` object using the `parse_time` method. This is useful for reading time data from external sources.

5. **Time Calculations**: The `TimeCalculator` class provides methods to manipulate time. Users can add or subtract time intervals from `datetime` objects, facilitating time arithmetic.

6. **Validation**: Before performing operations that depend on user input (like parsing a time string), the `is_time_valid` function can be called to ensure the input conforms to the expected format.

7. **Error Management**: Throughout these operations, error handling is in place to catch and manage exceptions, ensuring that the module’s functionality remains robust and user-friendly.

## Conclusion

The `time_utils.py` module is an integral part of the Savant ecosystem, designed with a focus on clarity, precision, and reusability. By encapsulating time-related functionalities within dedicated classes and functions, it enhances the overall modularity of the system. The design philosophy emphasizes single responsibility, robust error handling, and seamless integration with other modules, ensuring that time management is both efficient and reliable.

This README serves as a comprehensive guide to understanding the purpose, structure, and functionality of `time_utils.py`, equipping developers with the knowledge needed to effectively utilize this module within the Savant framework.