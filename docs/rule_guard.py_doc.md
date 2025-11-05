# README for `rule_guard.py`

## Overview

The `rule_guard.py` module serves as a critical component within the Savant ecosystem, functioning as a rule enforcement and validation layer. Its primary objective is to ensure that various rules governing data integrity, access control, and operational constraints are adhered to throughout the system. This document provides a comprehensive overview of the module, detailing its role, class and function purposes, design philosophy, error handling mechanisms, relationships with other modules, and internal flow.

## Role within Savant’s Modular Ecosystem

In Savant's architecture, `rule_guard.py` acts as a guardian of business logic and operational rules. It operates at the intersection of data handling and user interactions, ensuring that all operations comply with predefined rules. This module is particularly essential in environments where data integrity is paramount, such as financial systems, healthcare applications, and regulatory compliance frameworks.

The module is designed to be modular and extensible, allowing for easy integration with other components of the Savant ecosystem. It can be invoked by various services and controllers that require rule validation before proceeding with data manipulations or user actions.

## Classes and Functions

### 1. `RuleGuard`

#### Purpose
The `RuleGuard` class is the primary interface for rule validation within the module. It encapsulates the logic needed to evaluate rules against provided data.

#### Attributes
- `rules`: A list of rules that the `RuleGuard` will enforce.
- `data`: The data object against which the rules will be validated.

#### Methods
- `__init__(self, rules: List[Rule], data: Any)`: Initializes the `RuleGuard` with a set of rules and the data to validate.
- `validate(self) -> bool`: Iterates through the rules and applies them to the data. Returns `True` if all rules pass; otherwise, returns `False`.
- `get_errors(self) -> List[str]`: Returns a list of error messages for any rules that failed validation.

### 2. `Rule`

#### Purpose
The `Rule` class defines individual validation rules. Each rule can be associated with a specific validation function and can include parameters for more complex validation scenarios.

#### Attributes
- `name`: A string representing the name of the rule.
- `validation_func`: A callable that implements the validation logic.
- `params`: A dictionary of parameters that may be required by the validation function.

#### Methods
- `__init__(self, name: str, validation_func: Callable, params: Dict[str, Any] = None)`: Initializes a rule with a name, validation function, and optional parameters.
- `validate(self, data: Any) -> bool`: Executes the validation function with the provided data and parameters. Returns the result of the validation.

### 3. `ValidationError`

#### Purpose
The `ValidationError` class is a custom exception used to indicate validation failures. It encapsulates error messages and context to facilitate debugging.

#### Attributes
- `message`: A string describing the validation error.
- `context`: An optional dictionary providing additional context about the error.

#### Methods
- `__init__(self, message: str, context: Dict[str, Any] = None)`: Initializes a validation error with a message and optional context.

## Design Philosophy

The design of `rule_guard.py` adheres to several key principles:

1. **Modularity**: Each class and function is designed to perform a specific task, promoting separation of concerns. This modularity allows for easier testing, maintenance, and extension.

2. **Extensibility**: The `Rule` class can be easily extended to accommodate new types of validation logic. This flexibility is crucial in a dynamic environment where business rules may evolve.

3. **Clarity**: The naming conventions and structure of the code prioritize readability and clarity, making it easier for developers to understand and utilize the module.

4. **Error Transparency**: By defining a custom `ValidationError`, the module provides clear and actionable feedback when validation fails. This transparency aids in debugging and enhances the user experience.

## Error Handling

Error handling in `rule_guard.py` is primarily managed through the `ValidationError` class. When a rule fails validation, the `validate` method of the `Rule` class raises a `ValidationError`, which can include context to help identify the source of the issue. 

The `RuleGuard` class aggregates these errors and provides a method to retrieve them, ensuring that users can see all validation issues at once. This approach minimizes the risk of silent failures and encourages proactive error management.

### Example of Error Handling

```python
try:
    guard = RuleGuard(rules, data)
    if not guard.validate():
        errors = guard.get_errors()
        # Handle errors appropriately
except ValidationError as e:
    # Log or handle the validation error
```

## Relationships to Other Modules

`rule_guard.py` interacts with several other modules within the Savant ecosystem:

- **Data Models**: The module often receives data from various data models, validating them before they are processed or stored.
- **Controllers**: Controllers may invoke the `RuleGuard` to ensure that user inputs or actions comply with business rules before proceeding with further logic.
- **Logging**: Integration with a logging module may be employed to log validation errors for auditing and debugging purposes.

## Internal Flow

The internal flow of `rule_guard.py` can be summarized as follows:

1. **Initialization**: A `RuleGuard` instance is created with a list of `Rule` objects and the data to be validated.

2. **Validation Process**:
   - The `validate` method of `RuleGuard` is called.
   - For each `Rule` in the `rules` list, the `validate` method of the `Rule` class is invoked with the data.
   - If a rule fails, a `ValidationError` is raised, and the error message is captured.

3. **Error Retrieval**: After validation, the `get_errors` method of `RuleGuard` is called to retrieve any validation errors encountered during the process.

4. **Error Handling**: The calling context can then handle these errors as needed, whether by logging them, displaying them to the user, or taking corrective actions.

### Example Flow

```python
# Define rules
rules = [
    Rule("check_positive", check_positive_function),
    Rule("check_length", check_length_function, {"min": 5}),
]

# Data to validate
data = {"amount": 10, "name": "Savant"}

# Create RuleGuard instance
guard = RuleGuard(rules, data)

# Validate data
if not guard.validate():
    errors = guard.get_errors()
    # Handle errors
```

## Conclusion

The `rule_guard.py` module is a foundational element of the Savant ecosystem, ensuring that rules governing data integrity and operational constraints are enforced consistently. Through its modular design, clear error handling, and extensibility, it provides a robust framework for validating business logic across various applications. This README serves as a comprehensive guide for developers seeking to understand and utilize the capabilities of `rule_guard.py` effectively.