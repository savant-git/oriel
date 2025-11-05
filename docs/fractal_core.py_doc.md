# README for `fractal_core.py`

## Overview

The `fractal_core.py` module serves as a pivotal component within the Savant ecosystem, designed to facilitate the generation and manipulation of fractal structures. As part of Savant's modular architecture, this module encapsulates the core algorithms and data structures necessary for fractal computations, enabling users to create intricate visual representations of mathematical phenomena. This document provides a comprehensive overview of `fractal_core.py`, detailing its role, classes, functions, design philosophy, error handling, relationships with other modules, and internal flow.

## Role Within Savant’s Modular Ecosystem

The Savant ecosystem is built upon a modular framework that promotes separation of concerns, allowing for scalable and maintainable code. The `fractal_core.py` module is integral to this architecture, as it:

- **Encapsulates Fractal Logic**: It houses the algorithms necessary for generating various types of fractals, such as the Mandelbrot and Julia sets.
- **Provides Interfaces**: The module exposes a clear API for other components within Savant to interact with fractal data, ensuring ease of integration.
- **Facilitates Extensibility**: By adhering to design principles that promote modularity, `fractal_core.py` can be extended to include new fractal types or algorithms without significant refactoring.

## Classes and Functions

### Classes

#### 1. `Fractal`

The `Fractal` class serves as a base class for all fractal types. It encapsulates common properties and methods that are shared across different fractal implementations.

**Attributes:**
- `max_iterations`: Integer representing the maximum number of iterations for fractal calculations.
- `color_map`: A callable that defines how colors are assigned based on iteration counts.

**Methods:**
- `__init__(self, max_iterations=1000, color_map=default_color_map)`: Initializes a new fractal instance with specified parameters.
- `generate(self, x_min, x_max, y_min, y_max, width, height)`: Abstract method to be implemented by subclasses for generating fractal data.

#### 2. `Mandelbrot(Fractal)`

The `Mandelbrot` class extends the `Fractal` class to implement the Mandelbrot set algorithm.

**Methods:**
- `generate(self, x_min, x_max, y_min, y_max, width, height)`: Implements the specific logic to compute the Mandelbrot set over the specified range and resolution.

#### 3. `Julia(Fractal)`

Similar to the `Mandelbrot` class, the `Julia` class implements the Julia set algorithm.

**Methods:**
- `generate(self, x_min, x_max, y_min, y_max, width, height)`: Contains the logic for generating the Julia set based on a specific complex parameter.

### Functions

#### 1. `default_color_map(iteration_count)`

A utility function that provides a default color mapping based on the number of iterations. This function is used by the `Fractal` class to assign colors to points in the fractal.

#### 2. `create_fractal(fractal_type, **kwargs)`

A factory function that instantiates the appropriate fractal class based on the `fractal_type` argument. It accepts additional parameters via `kwargs` to customize the fractal instance.

## Design Philosophy

The design philosophy of `fractal_core.py` emphasizes:

- **Separation of Concerns**: Each fractal type is encapsulated within its own class, allowing for clear delineation of responsibilities.
- **Extensibility**: New fractal types can be added with minimal disruption to existing code, adhering to the Open/Closed Principle.
- **Clarity and Readability**: Code is written with an emphasis on clarity, using descriptive names and comments to enhance understanding.
- **Performance**: Algorithms are optimized for performance, particularly in the context of iterative calculations, which are central to fractal generation.

## Error Handling

Error handling in `fractal_core.py` is managed through:

- **Input Validation**: Functions and methods validate inputs to ensure they meet expected criteria. For instance, `max_iterations` must be a positive integer.
- **Exception Raising**: Custom exceptions are raised when invalid parameters are encountered. For example, if a user attempts to create a fractal with a negative resolution, a `ValueError` is raised with a descriptive message.
- **Graceful Degradation**: In scenarios where errors occur during fractal generation, the module is designed to handle exceptions gracefully, allowing the application to continue running without crashing.

## Relationships to Other Modules

`fractal_core.py` interacts with several other modules within the Savant ecosystem:

- **`visualization.py`**: This module utilizes the output from `fractal_core.py` to render fractals visually. It takes the generated data and applies graphical techniques to display the fractals in a user-friendly manner.
- **`input_handler.py`**: This module manages user inputs and passes relevant parameters to `create_fractal`. It ensures that user-defined settings are validated before being forwarded to the fractal generation process.
- **`color_maps.py`**: This module defines various color mapping functions that can be used in conjunction with the fractal classes. Users can specify custom color maps when instantiating fractals.

## Internal Flow

The internal flow of `fractal_core.py` can be summarized as follows:

1. **Initialization**: A user or external module calls `create_fractal(fractal_type, **kwargs)`, specifying the desired fractal type and parameters.
2. **Class Instantiation**: The factory function determines the appropriate class to instantiate (e.g., `Mandelbrot` or `Julia`) and creates an object of that class with the provided parameters.
3. **Fractal Generation**: The `generate` method of the instantiated fractal class is invoked, which performs the iterative calculations necessary to generate the fractal data.
4. **Color Mapping**: As the fractal data is generated, the `default_color_map` or a user-defined color map is applied to determine the color of each point based on the number of iterations.
5. **Output**: The generated fractal data is returned to the caller, which may then pass it to the `visualization.py` module for rendering.

### Example Usage

Here is an example of how to use the `fractal_core.py` module:

```python
from fractal_core import create_fractal

# Create a Mandelbrot fractal
mandelbrot = create_fractal('Mandelbrot', max_iterations=1000, color_map=my_custom_color_map)
fractal_data = mandelbrot.generate(-2.0, 1.0, -1.5, 1.5, 800, 600)

# Pass the data to the visualization module
from visualization import render_fractal
render_fractal(fractal_data)
```

## Conclusion

The `fractal_core.py` module is a cornerstone of the Savant ecosystem, providing essential functionality for fractal generation. Through its well-defined classes and functions, it encapsulates the complexity of fractal mathematics while offering a user-friendly interface for integration with other components. The design philosophy prioritizes clarity, extensibility, and performance, ensuring that the module can evolve alongside the needs of its users. By adhering to robust error handling practices and maintaining clear relationships with other modules, `fractal_core.py` stands as a testament to the principles of modular software design within the Savant framework.