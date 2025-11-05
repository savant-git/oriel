# README for `shard_registry.py`

## Overview

The `shard_registry.py` module is a critical component of the Savant ecosystem, designed to manage and maintain the state of sharded data across distributed systems. This document provides an in-depth exploration of the module, detailing its role, classes, functions, design philosophy, error handling, relationships with other modules, and internal flow.

## Role within Savant’s Modular Ecosystem

In a distributed architecture, data is often partitioned into smaller, manageable pieces called shards. The `shard_registry.py` module serves as the authoritative source for tracking the metadata and state of these shards. This includes information such as which nodes own which shards, the health of each shard, and the overall distribution of data. By centralizing shard management, `shard_registry.py` facilitates efficient data access, load balancing, and fault tolerance within Savant.

## Design Philosophy

The design philosophy of `shard_registry.py` is grounded in the principles of modularity, scalability, and robustness. Each component of the module is designed to be:

1. **Modular**: Classes and functions are encapsulated, promoting reusability and separation of concerns.
2. **Scalable**: The architecture supports the dynamic addition and removal of shards and nodes, allowing for seamless scaling of the system.
3. **Robust**: Error handling is integrated at multiple levels to ensure that the system can gracefully recover from failures.

## Classes and Functions

### Classes

#### 1. `ShardRegistry`

**Purpose**: The `ShardRegistry` class is the core of the module. It manages the lifecycle of shards, including their creation, deletion, and state management.

**Key Attributes**:
- `shards`: A dictionary mapping shard identifiers to shard metadata.
- `nodes`: A dictionary mapping node identifiers to their respective shard assignments.

**Key Methods**:
- `add_shard(shard_id, node_id)`: Adds a new shard to the registry, assigning it to a specified node.
- `remove_shard(shard_id)`: Removes a shard from the registry, updating the node assignments accordingly.
- `get_shard_info(shard_id)`: Retrieves metadata for a specified shard.
- `get_all_shards()`: Returns a list of all shards managed by the registry.
- `rebalance_shards()`: Reassigns shards across nodes to ensure balanced load distribution.

#### 2. `Shard`

**Purpose**: The `Shard` class encapsulates the properties and behaviors of an individual shard.

**Key Attributes**:
- `shard_id`: Unique identifier for the shard.
- `node_id`: Identifier of the node currently hosting the shard.
- `status`: Current health status of the shard (e.g., healthy, degraded, offline).

**Key Methods**:
- `update_status(new_status)`: Updates the health status of the shard.
- `get_status()`: Returns the current status of the shard.

### Functions

#### 1. `initialize_registry()`

**Purpose**: Initializes the shard registry with default values and settings. This function is typically called at the startup of the application.

#### 2. `load_registry_state(file_path)`

**Purpose**: Loads the state of the shard registry from a persistent storage file. This function is essential for recovering the state after a system restart.

#### 3. `save_registry_state(file_path)`

**Purpose**: Saves the current state of the shard registry to a persistent storage file. This is crucial for maintaining consistency across system restarts.

## Error Handling

Error handling in `shard_registry.py` is implemented using Python's built-in exception handling mechanisms. The module anticipates several types of errors, including:

- **KeyErrors**: Raised when attempting to access a shard or node that does not exist. Handled gracefully by returning a default value or raising a custom exception.
- **IOErrors**: Occur during file operations (loading/saving state). These are caught and logged, with fallback mechanisms to ensure the system remains operational.
- **ValueErrors**: Triggered by invalid input values, such as incorrect shard IDs. These are validated before processing to prevent runtime errors.

Custom exceptions are defined to provide more context for errors specific to shard operations, such as `ShardNotFoundError` and `NodeNotFoundError`.

## Relationships to Other Modules

The `shard_registry.py` module interacts closely with several other modules within the Savant ecosystem:

- **Data Storage Module**: Collaborates with data storage components to ensure that shard metadata is accurately reflected in persistent storage.
- **Node Management Module**: Works in tandem with node management to update shard assignments based on node health and availability.
- **Load Balancer Module**: Provides shard information to the load balancer, which uses this data to distribute requests evenly across nodes.

These relationships are facilitated through well-defined interfaces and callbacks, ensuring that `shard_registry.py` can communicate effectively with other components.

## Internal Flow

The internal flow of `shard_registry.py` can be summarized in the following steps:

1. **Initialization**: The module is initialized by calling `initialize_registry()`, which sets up the internal data structures.
  
2. **Loading State**: If the application is recovering from a previous state, `load_registry_state(file_path)` is invoked to populate the shard registry with existing data.

3. **Shard Management**:
   - When a new shard is created, `add_shard(shard_id, node_id)` is called, updating the internal `shards` and `nodes` dictionaries.
   - To remove a shard, `remove_shard(shard_id)` is invoked, which also updates the node assignments.
   - The health of shards is monitored, and updates are made using the `update_status(new_status)` method of the `Shard` class.

4. **Rebalancing**: Periodically, `rebalance_shards()` is executed to ensure that shards are evenly distributed across nodes.

5. **Saving State**: Before the application shuts down or at regular intervals, `save_registry_state(file_path)` is called to persist the current state of the shard registry.

## Conclusion

The `shard_registry.py` module is a vital component of the Savant architecture, providing robust management of sharded data in a distributed environment. Through its well-defined classes and functions, it ensures that shards are efficiently tracked, managed, and rebalanced, contributing to the overall performance and reliability of the system. By adhering to a clear design philosophy and implementing comprehensive error handling, `shard_registry.py` stands as a testament to the principles of modular and scalable software design within the Savant ecosystem.