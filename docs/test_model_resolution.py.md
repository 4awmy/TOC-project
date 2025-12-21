# Documentation for `test_model_resolution.py`

## Overview
`test_model_resolution.py` is a **Unit Test** script designed to verify the robustness of the AI model selection logic.

## Purpose
The Google Gemini API occasionally deprecates model versions (e.g., `gemini-1.5-flash-latest`), causing `404 Not Found` errors. To fix this, the application implements a dynamic resolution strategy (`_resolve_model_name`) in `ai_handler.py`.

This script mocks the `google.generativeai` library to ensure that the resolution logic works correctly under various scenarios.

## Test Cases
The script uses `unittest` and `unittest.mock` to simulate:
1.  **Exact Match**: The preferred model exists.
2.  **Variant Match**: Only a variant (e.g., `gemini-1.5-flash-001`) exists.
3.  **Fallback**: The preferred model is missing, so it falls back to a safe default (`gemini-pro`).
4.  **Empty List**: The API returns no models (edge case).

## Usage
Run this script to verify the logic without making actual API calls:
```bash
python test_model_resolution.py
```
