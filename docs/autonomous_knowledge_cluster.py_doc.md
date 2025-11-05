# README for `autonomous_knowledge_cluster.py`

## Overview

The `autonomous_knowledge_cluster.py` module serves as a pivotal component within the Savant ecosystem, designed to autonomously enhance the knowledge base by leveraging intelligent search capabilities, recursive topic discovery, and content synthesis. This module embodies the principles of clarity, precision, and lyrical elegance, adhering to the Savant Documentation Doctrine. With its robust architecture, it integrates seamlessly with other Savant modules, thus fostering a cohesive environment for knowledge management and retrieval.

## Core Purpose

The core purpose of the `autonomous_knowledge_cluster.py` module is to automate the process of knowledge acquisition and synthesis. It achieves this through several key functionalities:

1. **API-based Intelligent Search**: The module utilizes external APIs (Brave Search and SerpAPI) to perform intelligent searches based on predefined topics, ensuring that the retrieved content is relevant and trustworthy.

2. **Recursive Topic Discovery**: By expanding upon a set of primary topics, the module generates a broader range of search queries, thereby enhancing the depth and breadth of knowledge acquisition.

3. **Open-license Content Synthesis**: The module processes and synthesizes content from various sources, storing it in a structured format that facilitates easy retrieval and further processing.

4. **Integrated Cloud Sync Trigger**: The module includes functionality to synchronize the acquired knowledge with a cloud service, ensuring that the knowledge base remains up-to-date and accessible across different platforms.

## Detailed Analysis of Classes and Functions

The module is structured around a series of functions, each serving a specific purpose. Below is a detailed analysis of each function:

### 1. `iso()`

```python
def iso(): 
    return datetime.now(timezone.utc).isoformat()
```

- **Purpose**: Returns the current timestamp in ISO 8601 format.
- **Usage**: Primarily used for logging and metadata purposes when creating new knowledge entries.

### 2. `brave_search(query)`

```python
def brave_search(query):
    if not BRAVE_KEY: return []
    try:
        r = requests.get(
            "https://api.search.brave.com/res/v1/web/search",
            params={"q": query, "count": 10},
            headers={"X-Subscription-Token": BRAVE_KEY, "User-Agent": "Savant-KnowledgeBot/2.0"},
            timeout=10,
        )
        data = r.json()
        return [i["url"] for i in data.get("web", {}).get("results", []) if any(d in i["url"] for d in SAFE_DOMAINS)]
    except Exception as e:
        footer("Error.", "error")
        return []
```

- **Purpose**: Performs a search using the Brave Search API and returns a list of URLs that match the query.
- **Error Handling**: Catches exceptions and logs an error message while returning an empty list if the search fails.

### 3. `serpapi_search(query)`

```python
def serpapi_search(query):
    if not SERP_KEY: return []
    try:
        r = requests.get("https://serpapi.com/search", params={"engine": "google", "q": query, "api_key": SERP_KEY}, timeout=10)
        data = r.json()
        return [i["link"] for i in data.get("organic_results", []) if any(d in i["link"] for d in SAFE_DOMAINS)]
    except Exception as e:
        footer("Error.", "error")
        return []
```

- **Purpose**: Conducts a search using the SerpAPI and returns relevant URLs.
- **Error Handling**: Similar to `brave_search`, it handles exceptions gracefully and logs errors.

### 4. `html_search(query)`

```python
def html_search(query):
    url = f"https://duckduckgo.com/html/?q={quote_plus(query)}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, timeout=10, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        return [a["href"] for a in soup.find_all("a", href=True) if any(d in a["href"] for d in SAFE_DOMAINS)]
    except Exception:
        return []
```

- **Purpose**: Uses DuckDuckGo's HTML search to find URLs based on the query.
- **Error Handling**: Returns an empty list upon failure, without logging, which could be improved for better traceability.

### 5. `extract_text(html: str)`

```python
def extract_text(html: str):
    soup = BeautifulSoup(html, "html.parser")
    for bad in soup(["script", "style", "noscript"]): bad.decompose()
    text = "\n".join([ln.strip() for ln in soup.get_text("\n").splitlines() if ln.strip()])
    return re.sub(r"\n{3,}", "\n\n", text)
```

- **Purpose**: Extracts and cleans text content from HTML, removing unwanted elements.
- **Usage**: Essential for preparing the content for storage and further processing.

### 6. `fetch_url(url: str)`

```python
def fetch_url(url: str):
    try:
        r = requests.get(url, headers={"User-Agent": "Savant-KnowledgeBot/2.0"}, timeout=15)
        if r.status_code == 200 and any(d in url for d in SAFE_DOMAINS):
            text = extract_text(r.text)
            if len(text) > 400:
                hid = sha1_str(url)
                path = RAW / f"{hid}.txt"
                if not path.exists():
                    path.write_text(text, encoding="utf-8")
                    print(f"📚 Saved {url}")
                    return True
    except Exception:
        pass
    return False
```

- **Purpose**: Fetches content from a given URL, extracts the text, and saves it if valid.
- **Error Handling**: Catches exceptions silently, which may lead to undetected issues.

### 7. `expand_topics(seed_topics)`

```python
def expand_topics(seed_topics):
    new_topics = []
    for t in seed_topics:
        parts = t.split()
        if len(parts) > 2:
            new_topics.append(" ".join(parts[:2]))
            new_topics.append("advanced " + t)
            new_topics.append(t + " for beginners")
            new_topics.append("latest trends in " + parts[0])
    return list(dict.fromkeys(seed_topics + new_topics))
```

- **Purpose**: Expands a list of seed topics into more specific sub-topics for broader search coverage.
- **Usage**: Enhances the search queries to capture a wider array of relevant content.

### 8. `synthesize_shards()`

```python
def synthesize_shards():
    files = sorted(RAW.glob("*.txt"))
    total_added = 0
    for fp in files:
        text = fp.read_text(encoding="utf-8", errors="ignore")
        chunks = chunk_text(text, target_tokens=900, overlap_tokens=120)
        doms = infer_domains(text)
        for ch in chunks:
            hid = sha1_str(ch)
            for d in doms:
                out = SHRD / d; out.mkdir(parents=True, exist_ok=True)
                path = out / f"{hid}.json"
                if path.exists(): continue
                save_json(path, {"id": hid, "domain": d, "source": str(fp), "created": iso(), "body": ch})
                total_added += 1
    lvl = level_from_shards(sum(1 for _ in SHRD.rglob("*.json")))
    log_event("auto_synthesis_complete", {"added": total_added, "level": lvl})
    footer("Complete.", "done")
```

- **Purpose**: Processes raw text files, chunks them, and saves them as JSON shards for structured storage.
- **Error Handling**: Implicitly handles errors by checking for existing files and gracefully skipping them.

### 9. `main()`

```python
def main():
    header("Savant Core", "1.0", "Restored aesthetic", "core")
    topics = expand_topics(PRIMARY_TOPICS)
    print(f"📚 Topics expanded to {len(topics)} total.")
    urls = []
    for q in topics:
        found = brave_search(q) or serpapi_search(q) or html_search(q)
        urls.extend(found)
        time.sleep(random.uniform(1.5, 3.0))
    urls = list(dict.fromkeys(urls))
    print(f"🌐 Found {len(urls)} total URLs.")
    added = 0
    for u in urls:
        if fetch_url(u): added += 1
        time.sleep(random.uniform(1.5, 3.0))
    footer("Complete.", "done")
    synthesize_shards()
    os.system(f"python3 ~/savant/services/scripts/intelligence_cluster/cloud_uplink.py || true")
    print("☁️  Cloud sync complete.")
    print("✨ Knowledge expansion finished.")
```

- **Purpose**: The main execution flow of the module, orchestrating the entire knowledge acquisition process.
- **Integration**: Calls other functions to perform searches, fetch content, and synthesize knowledge.
- **Error Handling**: Limited error handling; improvements could include logging failures in fetching URLs.

## Error-Handling Patterns and Architectural Decisions

The error-handling patterns in `autonomous_knowledge_cluster.py` primarily utilize try-except blocks to catch exceptions during API calls and content fetching. However, there are areas for improvement:

1. **Logging**: While some functions log errors, others do not. A consistent logging mechanism should be implemented to facilitate debugging and monitoring.

2. **Silent Failures**: Some functions return empty lists or silently pass on exceptions, which can lead to undetected issues. It is advisable to log these events for better traceability.

3. **Graceful Degradation**: The module is designed to continue functioning even if certain searches fail, which is a positive architectural decision. However, it could benefit from notifying the user of such failures.

4. **Modularity**: The module is well-structured, with distinct functions handling specific tasks. This modularity enhances readability and maintainability.

## Integration Points with Other Savant Modules

The `autonomous_knowledge_cluster.py` module integrates with several other components within the Savant ecosystem:

1. **`cloud_uplink.py`**: This module is invoked at the end of the knowledge synthesis process to synchronize the newly acquired knowledge with the cloud, ensuring that the knowledge base is always current.

2. **`shard_tools`**: Functions from this module are utilized for text chunking, domain inference, and JSON saving, allowing for efficient data handling and storage.

3. **Logging Services**: The module utilizes logging functions (e.g., `log_event`) to record significant events and errors, contributing to the overall observability of the Savant ecosystem.

## Historical Rationale and Design Philosophy

The design of `autonomous_knowledge_cluster.py` is rooted in the need for an automated, scalable solution for knowledge acquisition in an increasingly complex digital landscape. As the volume of information grows, the ability to efficiently gather, synthesize, and store knowledge becomes paramount.

### Key Design Principles

1. **Automation**: The module is designed to minimize manual intervention, allowing for continuous knowledge expansion without user input.

2. **Scalability**: By leveraging external APIs and cloud synchronization, the module can scale its operations to accommodate growing datasets.

3. **User-Centric Design**: The module aims to provide relevant and trustworthy content, ensuring that users receive high-quality information.

4. **Clarity and Precision**: Adhering to the Savant Documentation Doctrine, the module prioritizes clear and precise documentation, making it easier for developers and users to understand its functionality.

5. **Flexibility**: The integration with multiple search APIs allows for fallback mechanisms, ensuring that the module remains functional even if one service is unavailable.

## Conclusion

The `autonomous_knowledge_cluster.py` module stands as a testament to the Savant ecosystem's commitment to intelligent knowledge management. With its robust architecture, thoughtful design, and seamless integration with other components, it embodies the principles of automation, scalability, and user-centric design. As the digital landscape continues to evolve, this module will play a crucial role in ensuring that knowledge remains accessible, relevant, and actionable.