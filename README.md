# Automata & Formal Language Studio

A powerful AI-powered tool for exploring Theory of Computation concepts, including Regular Languages, Automata, and Regex.

## Features

1.  **Define Languages (AI Analysis)**: Describe a formal language in plain English (e.g., "Strings ending in 101"). The AI determines if it is Regular, provides a Regex, and explains the reasoning.
2.  **Test Strings**: Check if specific strings belong to the defined language, with detailed acceptance/rejection reasons.
3.  **Batch Testing**: Validate multiple strings at once using manual input, CSV uploads, or hardcoded samples.
4.  **Automata Operations**:
    *   **NFA to DFA Conversion**: Convert Non-Deterministic Finite Automata to Deterministic ones.
    *   **NFA to Regex**: Convert an NFA to a Regular Expression.
    *   **DFA Minimization**: Minimize a DFA to its most efficient state representation.

## Setup & Installation

1.  **Prerequisites**: Python 3.8+
2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Run the Application**:
    ```bash
    streamlit run app.py
    ```

## File Structure

*   **`app.py`**: The main entry point for the Streamlit GUI. It handles the user interface, state management, and interaction with the `LanguageProcessor`.
*   **`logic.py`**: Contains the `LanguageProcessor` class. It acts as the business logic layer, bridging the UI and the AI handler. It manages the current language state and processes string checks.
*   **`ai_handler.py`**: Handles direct communication with the Google Gemini API. It constructs prompts for analyzing languages, checking strings, and performing automata operations.
*   **`requirements.txt`**: Lists all Python dependencies required to run the project.

## Configuration

The application requires a **Google Gemini API Key**.
*   You can set it via the environment variable `GOOGLE_API_KEY`.
*   Alternatively, you can enter it directly in the application sidebar.

## Technologies

*   **Python**: Core programming language.
*   **Streamlit**: Web framework for the GUI.
*   **Google Gemini API**: LLM provider for analysis and logic.
