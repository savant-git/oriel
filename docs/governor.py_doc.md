# README for `governor.py`

## Overview

The `governor.py` module serves as a pivotal component within the Savant ecosystem, acting as a unified controller for the Deep Research, Enhancement, and Personality engines. This module is designed to facilitate complex interactions between various subsystems, ensuring that research and enhancement tasks are executed efficiently and effectively. By providing a streamlined interface for users to engage with these engines, `governor.py` embodies the principles of clarity, precision, and lyrical elegance that define the Savant Documentation Doctrine.

## Core Purpose

At its core, `governor.py` is responsible for managing the operational cycles of the Savant system. It allows users to select between two primary modes of operation: conducting deep research on a specified topic or enhancing a given file or directory. This dual functionality makes it a crucial element in the Savant architecture, enabling users to leverage the full capabilities of the underlying engines while maintaining an intuitive user experience.

## Detailed Analysis of Classes and Functions

### Class: `SavantGovernor`

The `SavantGovernor` class encapsulates the functionality of the governor module. Below, we dissect its components in detail.

#### Constructor: `__init__(self)`

The constructor initializes the `SavantGovernor` instance, setting up the necessary engines and publishing an initialization message to the event bus.

```python
def __init__(self):
    self.research_engine = DeepResearchEngine()
    self.enhancement_engine = EnhancementEngine()
    self.bridge = run_bridge()

    publish("governor_init", {
        "status": "initialized",
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
```

- **Attributes**:
  - `self.research_engine`: An instance of `DeepResearchEngine`, responsible for conducting research tasks.
  - `self.enhancement_engine`: An instance of `EnhancementEngine`, responsible for enhancing files or directories.
  - `self.bridge`: A bridge hook for connecting to other components within the Savant ecosystem.

- **Event Publishing**: The constructor publishes an initialization event to the event bus, indicating that the governor has been successfully initialized.

#### Method: `run_cycle(self)`

The `run_cycle` method orchestrates the main functionality of the `SavantGovernor`, allowing users to choose between deep research and enhancement modes.

```python
def run_cycle(self):
    print("\n=== SAVANT GOVERNOR CORE ===")
    print("Choose Mode:")
    print("1. Deep Research")
    print("2. Enhancement")
    mode = input("> ").strip()
```

- **User Interaction**: The method prompts the user to select a mode of operation. Based on the user's input, it either initiates a research cycle or an enhancement cycle.

##### Sub-Functionality: Deep Research Mode

If the user selects deep research, the following sequence occurs:

```python
if mode == "1":
    topic = input("Enter research topic: ").strip()
    print(f"🔍 Researching '{topic}'...")
    try:
        report_path, word_count = self.research_engine.conduct_research(topic)
        publish("research_cycle_complete", {
            "topic": topic,
            "words": word_count,
            "path": report_path,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        footer("Complete.", "done")
    except Exception as e:
        publish("research_cycle_error", {"topic": topic, "error": str(e)})
        print(f"❌ Research failed: {e}")
```

- **Research Execution**: The method captures the research topic from the user and invokes the `conduct_research` method of the `DeepResearchEngine`.
- **Error Handling**: If an exception occurs during research, it is caught, and an error message is published to the event bus.

##### Sub-Functionality: Enhancement Mode

If the user opts for enhancement, the following sequence is executed:

```python
elif mode == "2":
    target = input("Enter file or directory to enhance: ").strip()
    print(f"⚙ Enhancing {target}...")
    try:
        modified = self.enhancement_engine.enhance(target)
        publish("enhancement_cycle_complete", {
            "target": target,
            "modified": modified,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        footer("Complete.", "done")
    except Exception as e:
        publish("enhancement_cycle_error", {"target": target, "error": str(e)})
        print(f"❌ Enhancement failed: {e}")
```

- **Enhancement Execution**: The method captures the target file or directory from the user and invokes the `enhance` method of the `EnhancementEngine`.
- **Error Handling**: Similar to the research mode, any exceptions are caught and published to the event bus.

##### Invalid Selection Handling

If the user makes an invalid selection, the following logic is executed:

```python
else:
    publish("governor_invalid_selection", {
        "selection": mode,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    print("⚠ Invalid selection.")
```

- **Event Publishing**: An event is published to indicate that the user made an invalid selection, allowing for better tracking and debugging.

### Execution Block

The module concludes with an execution block that instantiates the `SavantGovernor` and initiates the core cycle.

```python
if __name__ == "__main__":
    governor = SavantGovernor()
    governor.run_cycle()
```

This ensures that the governor is only executed when the module is run as a standalone script, promoting modularity and reusability.

## Error-Handling Patterns and Architectural Decisions

The error-handling strategy employed in `governor.py` revolves around the use of try-except blocks, allowing the module to gracefully handle exceptions that may arise during research or enhancement tasks. This design decision enhances the robustness of the module, ensuring that users receive informative feedback rather than abrupt crashes.

### Dynamic Import Recovery

The module also incorporates a dynamic import recovery mechanism, which attempts to resolve module import errors by extending the system path. This self-healing approach minimizes downtime and enhances the user experience by ensuring that the necessary components are available for execution.

```python
try:
    from savant.services.scripts.personality_engine.deep_research.research_core import DeepResearchEngine
    from savant.services.scripts.personality_engine.enhancement_engine.enhancement_core import EnhancementEngine
    from savant.services.scripts.personality_engine.governor_core.governor_bridge_hook import run_bridge
    from savant.services.event_bus.event_bus_core import publish
except ModuleNotFoundError as e:
    print(f"⚠ Import error: {e}")
    print("🔧 Attempting self-healing import patch...")
    sys.path.extend([
        os.path.join(BASE_PATH, "services"),
        os.path.join(BASE_PATH, "services", "scripts", "personality_engine"),
    ])
    from savant.services.scripts.personality_engine.deep_research.research_core import DeepResearchEngine
    from savant.services.scripts.personality_engine.enhancement_engine.enhancement_core import EnhancementEngine
    from savant.services.scripts.personality_engine.governor_core.governor_bridge_hook import run_bridge
    from savant.services.event_bus.event_bus_core import publish
```

This pattern reflects a forward-thinking architectural decision that prioritizes system resilience and user satisfaction.

## Integration Points with Other Savant Modules

The `governor.py` module integrates seamlessly with several other components of the Savant ecosystem:

- **Deep Research Engine**: Facilitates the execution of research tasks, enabling users to delve into specific topics and generate reports.
- **Enhancement Engine**: Provides the capability to enhance files or directories, thereby improving their quality or functionality.
- **Event Bus**: The module publishes various events to the event bus, allowing other components to react to changes in state, such as the completion of a research cycle or the occurrence of an error.

These integration points underscore the collaborative nature of the Savant ecosystem, where modules work in concert to deliver a cohesive user experience.

## Historical Rationale and Design Philosophy

The design of `governor.py` is rooted in a philosophy that emphasizes clarity, precision, and user-centric functionality. The module was developed in response to the need for a unified controller that could streamline interactions between the various engines within the Savant framework.

Historically, the evolution of the Savant ecosystem has been characterized by a commitment to modularity and extensibility. By encapsulating the core functionalities of research and enhancement within the `SavantGovernor`, the design allows for future enhancements and integrations without compromising the integrity of the overall system.

The lyrical cadence of the module's documentation reflects a broader commitment to creating a user experience that is not only functional but also engaging. This approach aligns with the overarching goals of the Savant project: to empower users through intelligent automation while maintaining a sense of artistry in technical communication.

## Conclusion

In summary, the `governor.py` module stands as a cornerstone of the Savant ecosystem, facilitating essential interactions between deep research and enhancement engines. Through careful design, robust error handling, and seamless integration with other components, it exemplifies the principles of clarity and precision that define the Savant Documentation Doctrine. As the Savant project continues to evolve, `governor.py` will undoubtedly play a crucial role in shaping the future of intelligent automation and user engagement.