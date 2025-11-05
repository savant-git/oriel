# README for `semantic_search.py`

## Overview

The `semantic_search.py` module is a pivotal component of the Savant ecosystem, designed to facilitate advanced semantic search capabilities. By leveraging natural language processing (NLP) techniques, this module allows users to retrieve information based on meaning rather than mere keyword matching. This README provides a comprehensive overview of the module, detailing its role, classes, functions, design philosophy, error handling, relationships with other modules, and internal flow.

## Role within Savant’s Modular Ecosystem

Within Savant, `semantic_search.py` serves as an interface between user queries and the underlying data storage. It enhances the search functionality by interpreting user intent, allowing for more relevant results. This module integrates seamlessly with other components of Savant, such as the data ingestion module and the user interface, ensuring a cohesive experience for users.

## Class and Function Overview

### Classes

#### 1. `SemanticSearch`
The `SemanticSearch` class is the core of the module, encapsulating all functionalities related to semantic search.

**Attributes:**
- `model`: An instance of a pre-trained NLP model (e.g., BERT, GPT) used for encoding queries and documents.
- `index`: A data structure (often a vector space model) that stores embeddings of documents for efficient retrieval.
- `threshold`: A float value that determines the minimum similarity score for a result to be considered relevant.

**Methods:**
- `__init__(self, model_name: str, threshold: float = 0.7)`: Initializes the `SemanticSearch` instance, loading the specified NLP model and setting the threshold.
- `index_documents(self, documents: List[str])`: Accepts a list of documents, encodes them using the NLP model, and stores their embeddings in the index.
- `search(self, query: str) -> List[Tuple[str, float]]`: Accepts a user query, encodes it, and retrieves a list of documents ranked by semantic similarity, filtered by the threshold.
- `set_threshold(self, threshold: float)`: Updates the threshold value for filtering results.

#### 2. `EmbeddingModel`
The `EmbeddingModel` class is responsible for managing the NLP model used for encoding text.

**Attributes:**
- `model`: The loaded NLP model.
- `tokenizer`: The tokenizer associated with the model to preprocess text.

**Methods:**
- `__init__(self, model_name: str)`: Loads the specified model and tokenizer.
- `encode(self, texts: List[str]) -> np.ndarray`: Encodes a list of texts into their respective embeddings.

### Functions

#### 1. `load_model(model_name: str) -> EmbeddingModel`
This function is responsible for loading an NLP model based on the provided name. It returns an instance of the `EmbeddingModel` class.

#### 2. `calculate_similarity(embedding_a: np.ndarray, embedding_b: np.ndarray) -> float`
Calculates the cosine similarity between two embeddings. This function is utilized within the `search` method of the `SemanticSearch` class to rank documents.

## Design Philosophy

The design philosophy of `semantic_search.py` is grounded in modularity, clarity, and efficiency. Each class and function is designed to perform a single responsibility, adhering to the Single Responsibility Principle (SRP). This modularity allows for easy maintenance and testing of individual components.

### Key Principles:
- **Modularity**: Each class and function is self-contained, promoting reusability and separation of concerns.
- **Clarity**: Code is written with clear naming conventions and documentation, ensuring that the purpose of each component is easily understood.
- **Efficiency**: The module is optimized for performance, particularly in the encoding and retrieval processes, to handle large datasets effectively.

## Error Handling

Error handling in `semantic_search.py` is implemented using Python's built-in exception handling mechanisms. The module anticipates potential issues and raises appropriate exceptions to inform users of errors.

### Key Error Handling Strategies:
- **Model Loading Errors**: When loading an NLP model, if the model name is incorrect or the model is unavailable, a `ModelLoadingError` is raised.
- **Input Validation**: Functions validate inputs to ensure they meet expected formats. For example, if a non-list type is passed to `index_documents`, a `TypeError` is raised.
- **Threshold Validation**: The `set_threshold` method checks if the threshold is within a valid range (0 to 1) and raises a `ValueError` if it is not.

## Relationships to Other Modules

The `semantic_search.py` module interacts with several other components within the Savant ecosystem:

- **Data Ingestion Module**: This module is responsible for collecting and preprocessing data. The `index_documents` method in `SemanticSearch` is often called after data ingestion to populate the index with document embeddings.
- **User Interface Module**: The UI module communicates with `semantic_search.py` to process user queries and display results. It invokes the `search` method to retrieve relevant documents based on user input.
- **Logging Module**: Throughout `semantic_search.py`, logging is employed to record significant events, errors, and performance metrics, aiding in debugging and monitoring.

## Internal Flow

The internal flow of `semantic_search.py` can be summarized in the following steps:

1. **Initialization**: An instance of `SemanticSearch` is created, which in turn initializes an `EmbeddingModel` instance with the specified NLP model.
   
   ```python
   search_instance = SemanticSearch(model_name="bert-base-uncased")
   ```

2. **Document Indexing**: The user ingests documents into the system, which are then passed to the `index_documents` method. This method encodes each document and stores its embedding in the index.

   ```python
   documents = ["Document 1 text.", "Document 2 text."]
   search_instance.index_documents(documents)
   ```

3. **Query Processing**: When a user submits a query, the `search` method is invoked. The query is encoded into an embedding using the `EmbeddingModel`.

   ```python
   results = search_instance.search("What is Document 1 about?")
   ```

4. **Similarity Calculation**: The encoded query is compared against the indexed document embeddings using cosine similarity. The results are filtered based on the predefined threshold.

5. **Result Retrieval**: The method returns a list of tuples containing the relevant documents and their similarity scores, which are then presented to the user through the UI.

## Conclusion

The `semantic_search.py` module is a robust and essential part of the Savant ecosystem, providing advanced semantic search capabilities. Through its carefully designed classes and functions, it offers a clear and efficient interface for users to retrieve information based on meaning. The module's design philosophy emphasizes modularity, clarity, and efficiency, ensuring that it can be easily maintained and extended. With effective error handling and seamless integration with other components, `semantic_search.py` stands as a testament to the power of modern NLP in enhancing information retrieval systems.