# README for `cloud_recover.py`

## Overview

The `cloud_recover.py` module serves as a pivotal component within the Savant ecosystem, designed to automate the process of downloading and restoring the latest export archive from Amazon S3. This module is essential for ensuring data integrity and availability, providing users with a seamless method to recover their data from the cloud. By leveraging the power of AWS S3, `cloud_recover.py` facilitates efficient data management and disaster recovery, aligning with Savant's overarching goal of enhancing user experience through automation and reliability.

## Core Purpose

At its core, `cloud_recover.py` is engineered to perform two primary functions:

1. **Download the Latest Archive**: The module connects to an S3 bucket specified in the environment variables, retrieves the most recent export archive, and saves it locally.
2. **Restore the Archive**: Once the archive is downloaded, it is unzipped and restored to a designated directory within the user's home directory. This functionality is crucial for users who need to recover data quickly and efficiently.

By automating these processes, `cloud_recover.py` minimizes manual intervention, reduces the potential for human error, and accelerates the recovery time for critical data.

## Detailed Analysis of Classes and Functions

### Imports and Initial Setup

The module begins by importing necessary libraries and modules:

```python
import os, boto3, zipfile, shutil
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
```

- **os**: Provides a way to use operating system-dependent functionality, such as reading environment variables.
- **boto3**: The Amazon Web Services (AWS) SDK for Python, which allows Python developers to write software that makes use of services like S3.
- **zipfile**: A module for reading and writing ZIP files, essential for handling the downloaded archives.
- **shutil**: A module that offers a number of high-level operations on files and collections of files, though it is not explicitly utilized in the current implementation.
- **datetime**: A module for manipulating dates and times, not directly used but imported for potential future enhancements.
- **pathlib**: A module for object-oriented filesystem paths, which simplifies path manipulations.
- **dotenv**: A module for loading environment variables from a `.env` file, ensuring sensitive information is not hard-coded.

### Constants and Environment Setup

The module defines key constants and initializes the environment:

```python
BASE = Path.home() / "savant"
EXPORTS = BASE / "archive"
EXPORTS.mkdir(parents=True, exist_ok=True)
load_dotenv(BASE / ".env")
```

- **BASE**: Represents the base directory for Savant, specifically within the user's home directory.
- **EXPORTS**: A subdirectory where downloaded archives will be stored. The `mkdir` method ensures that the directory is created if it does not already exist.
- **load_dotenv**: Loads environment variables from a `.env` file located in the base directory, facilitating secure access to AWS credentials.

### Function: `get_s3()`

```python
def get_s3():
    return boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1")
    )
```

The `get_s3()` function initializes a Boto3 S3 client using credentials sourced from environment variables. This function encapsulates the logic for establishing a connection to AWS S3, promoting reusability and separation of concerns. The default region is set to "us-east-1" if not specified.

### Function: `download_latest()`

```python
def download_latest():
    bucket = os.getenv("SAVANT_S3_BUCKET")
    if not bucket:
        footer("Error.", "error")
        return None
    s3 = get_s3()
    objs = s3.list_objects_v2(Bucket=bucket, Prefix="exports/")
    if "Contents" not in objs:
        footer("Error.", "error")
        return None
    latest = max(objs["Contents"], key=lambda x: x["LastModified"])
    key = latest["Key"]
    local = EXPORTS / Path(key).name
    print(f"⬇️  Downloading {key} → {local}")
    s3.download_file(bucket, key, str(local))
    footer("Complete.", "done")
    return local
```

The `download_latest()` function performs the following tasks:

1. **Bucket Retrieval**: It fetches the S3 bucket name from the environment variables. If the bucket is not specified, an error message is displayed, and the function returns `None`.
   
2. **List Objects**: It lists the objects in the specified S3 bucket under the "exports/" prefix. If no contents are found, it similarly returns an error.

3. **Determine Latest Archive**: It identifies the most recent archive based on the `LastModified` timestamp, utilizing the `max()` function.

4. **Download the Archive**: The selected archive is downloaded to the local `EXPORTS` directory, and a success message is displayed.

This function effectively encapsulates the logic for downloading the latest data, ensuring that users always retrieve the most current backup.

### Function: `restore_archive(archive_path: Path)`

```python
def restore_archive(archive_path: Path):
    dest = BASE
    print(f"🧩 Restoring archive → {dest}")
    with zipfile.ZipFile(archive_path, "r") as zf:
        zf.extractall(dest)
    footer("Complete.", "done")
```

The `restore_archive()` function is responsible for unzipping the downloaded archive and restoring its contents to the designated base directory. It performs the following:

1. **Logging**: It logs the restoration process, indicating the destination directory.
  
2. **Extraction**: Using the `zipfile.ZipFile` context manager, it opens the specified archive and extracts all its contents to the base directory.

3. **Completion Message**: Upon successful extraction, a completion message is displayed.

This function is critical for ensuring that the data is not only downloaded but also effectively restored for user access.

### Main Execution Block

```python
if __name__ == "__main__":
    header("Savant Core", "1.0", "Restored aesthetic", "core")
    latest = download_latest()
    if latest:
        restore_archive(latest)
        footer("Complete.", "done")
    else:
        footer("Error.", "error")
```

The main execution block serves as the entry point for the module. It performs the following tasks:

1. **Header Display**: It displays a header indicating the module's name and version.

2. **Download and Restore Logic**: It attempts to download the latest archive. If successful, it proceeds to restore the archive; otherwise, it logs an error.

This structure ensures that the module can be executed directly, providing a clear and user-friendly interface for data recovery.

## Error-Handling Patterns and Architectural Decisions

Error handling within `cloud_recover.py` is implemented primarily through conditional checks and logging messages. If any critical step fails, such as retrieving the bucket name or listing objects in S3, the module gracefully logs an error message using the `footer()` function. This approach ensures that users are informed of issues without causing abrupt terminations or unhandled exceptions.

The architectural decisions made in the design of this module prioritize modularity and clarity. Each function is focused on a single responsibility, making the codebase easier to maintain and extend. The use of environment variables for configuration enhances security by preventing the exposure of sensitive information in the code.

## Integration Points with Other Savant Modules

`cloud_recover.py` integrates seamlessly with other modules within the Savant ecosystem, particularly those that involve data exports and backups. The use of environment variables allows for easy configuration across different modules, ensuring that all components can operate cohesively.

Furthermore, the `header()` and `footer()` functions imported from `savant.services.scripts.system_core.command_header` provide a consistent user interface across Savant modules, enhancing the overall user experience.

## Historical Rationale and Design Philosophy

The development of `cloud_recover.py` was driven by the increasing need for reliable data recovery solutions in cloud environments. As organizations increasingly rely on cloud storage for critical data, the ability to quickly recover from data loss incidents becomes paramount.

The design philosophy behind this module emphasizes automation, reliability, and clarity. By automating the download and restoration processes, the module reduces the burden on users and minimizes the potential for human error. The clear structure and documentation ensure that users can easily understand and utilize the module, aligning with Savant's commitment to user-centric design.

In conclusion, `cloud_recover.py` stands as a testament to Savant's dedication to providing robust, user-friendly solutions for data management in the cloud. Its thoughtful design and integration within the Savant ecosystem make it an invaluable tool for users seeking to safeguard their data with efficiency and ease.