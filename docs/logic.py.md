# Documentation for `logic.py`

## Overview
`logic.py` acts as the **Business Logic Layer** or Orchestrator. It sits between the Frontend (`app.py`) and the AI Service (`ai_handler.py`).

## Key Classes

### `LanguageProcessor`
This class encapsulates the state of the "Current Language" being analyzed.

#### 1. State Management
-   Attributes:
    -   `current_description`: The natural language description (e.g., "Strings ending in 00").
    -   `is_regular`: Boolean flag.
    -   `regex`: The compiled Python Regex string (if regular).
    -   `analysis_explanation`: The AI's explanation.

#### 2. Workflow Orchestration
-   **Method**: `set_language(description)`
    -   Calls `AIHandler.analyze_language`.
    -   Updates internal state.
    -   Returns the analysis result to the UI.

#### 3. Hybrid String Processing
-   **Method**: `process_string(string)`
    -   **Path A (Regular)**: If the language is Regular and a Regex exists, it uses Python's `re.fullmatch` for deterministic, fast validation.
        -   If validation fails, it asks the AI to explain *why*.
    -   **Path B (Non-Regular)**: If the language is complex (e.g., "Balanced Parentheses"), it delegates the check entirely to `AIHandler.check_non_regular`.

## Dependencies
-   `ai_handler.py`: For AI services.
-   `re`: Standard Python Regex library.
