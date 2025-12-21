# Documentation for `ai_handler.py`

## Overview
`ai_handler.py` manages all interactions with the Google Gemini API. It is responsible for analyzing natural language descriptions of formal languages and verifying non-regular strings.

## Key Classes

### `AIHandler`
The main class for API interaction.

#### 1. Configuration & Security
-   **Initialization**: Can be initialized without an API key (lazy loading).
-   **Method**: `configure_api(api_key)`: Sets up the Gemini client at runtime.
-   **Method**: `_resolve_model_name()`:
    -   **Problem**: Specific model versions (like `gemini-1.5-flash-latest`) can be deprecated or region-locked, causing 404 errors.
    -   **Solution**: This method calls `genai.list_models()` to check which models are actually available to the user's account. It prioritizes `gemini-1.5-flash` but falls back gracefully if exact matches aren't found.

#### 2. Structured Outputs
To ensure reliability, the AI is restricted to returning strict JSON schemas using `typing.TypedDict`.

-   **Schemas**:
    -   `LanguageAnalysis`: `{ is_regular: bool, regex: str, explanation: str }`
    -   `StringCheck`: `{ accepted: bool, reason: str }`
-   **Implementation**: These schemas are passed to `generation_config` in `model.generate_content`, forcing the LLM to adhere to the format.

#### 3. Core Methods
-   `analyze_language(description)`: Determines if a description is Regular and extracts a Regex.
-   `check_non_regular(description, string)`: Acts as an "Oracle" for languages that cannot be converted to Regex (e.g., "Palindromes").
-   `explain_rejection(...)`: Generates a human-readable explanation for why a string failed validation.

## Dependencies
-   `google-generativeai`: The official Gemini SDK.
-   `typing`: For TypedDict definitions.
-   `json`: For parsing responses (though SDK handles most of this now via schemas).
