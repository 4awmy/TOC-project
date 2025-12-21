# Documentation for `main.py`

## Overview
`main.py` is the **Legacy Command Line Interface (CLI)** for the tool. It was the original prototype before the Streamlit web interface (`app.py`) was developed.

## Status
**Deprecated / Legacy**.
This file is retained for reference or for users who prefer a terminal-based interaction, but it does not support the latest visualization features found in the web app.

## Features
-   Interactive menu using the `rich` library.
-   Supports defining languages via text input.
-   Supports Batch Testing via CSV files (`test_inputs.csv`).
-   Uses `logic.py` for processing, sharing the same backend as the web app.

## Dependencies
-   `rich`: For terminal formatting.
-   `logic.py`: For language processing.
