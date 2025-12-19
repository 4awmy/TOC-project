# Automata & Formal Language Studio

A powerful AI-powered tool for exploring Theory of Computation concepts, including Regular Languages, Automata, and Regex. This project provides both a modern Web GUI and a legacy Command Line Interface.

## Features

1.  **Define Languages (AI Analysis)**: Describe a formal language in plain English (e.g., "Strings ending in 101"). The AI determines if it is Regular, provides a Regex, and explains the reasoning.
2.  **Test Strings**: Check if specific strings belong to the defined language, with detailed acceptance/rejection reasons.
3.  **Batch Testing**: Validate multiple strings at once using manual input, CSV uploads, or hardcoded samples.
4.  **Automata Operations**:
    *   **NFA to DFA Conversion**: Deterministically convert Non-Deterministic Finite Automata to Deterministic ones.
    *   **DFA Minimization**: Minimize a DFA to its most efficient state representation.
    *   **DFA to Regex**: Convert a DFA into a Regular Expression.
    *   **Regex to NFA**: Convert a Regular Expression into a Non-Deterministic Finite Automaton.
    *   **Visualization**: View diagrams of your automata.

## Setup & Installation

1.  **Prerequisites**: Python 3.8+
2.  **Install Python Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Install System Dependencies** (for visualization):
    *   This project uses Graphviz. Ensure it is installed on your system (e.g., `apt-get install graphviz` on Linux, or download from the official site for Windows/Mac).
4.  **Run the Application**:
    ```bash
    streamlit run app.py
    ```

## API Key Configuration

The application requires a **Google Gemini API Key** for the "Language Definition" features. You can obtain one from [Google AI Studio](https://aistudio.google.com/app/apikey).

You can configure the key in three ways (in order of priority):

### 1. Streamlit Secrets (Recommended for Local/Server)
This method allows the app to automatically detect the key as a "System Key", making it optional for end-users to provide their own.

1.  Create a folder named `.streamlit` in the project root.
2.  Inside it, create a file named `secrets.toml`.
3.  Add your key:
    ```toml
    GOOGLE_API_KEY = "your_actual_api_key_here"
    ```
    *(See `secrets.toml.example` for a template)*

### 2. Environment Variable
Set the `GOOGLE_API_KEY` environment variable in your terminal or deployment settings.
```bash
export GOOGLE_API_KEY="your_api_key"
streamlit run app.py
```

### 3. User Input (Sidebar)
If no system key is configured, the application will prompt the user to enter their own key in the sidebar.

## File Structure & Descriptions

Here is a detailed explanation of every file in the project:

### Core Application
*   **`app.py`**: The main entry point for the web application. Built with Streamlit, it manages the user interface, including tabs for language definition, batch testing, and automata operations. It handles user inputs and calls the appropriate logic handlers.
*   **`main.py`**: The legacy command-line interface (CLI) for the tool. It provides a text-based menu for defining languages and testing strings but lacks the advanced automata visualization features of the web app.

### Business Logic
*   **`logic.py`**: Contains the `LanguageProcessor` class. This is the bridge between the UI and the AI services. It manages the state of the "current language" being analyzed and orchestrates string testing against that language.
*   **`ai_handler.py`**: Handles all interactions with the Google Gemini API. It manages API key configuration and constructs the specific prompts used to analyze natural language descriptions of formal languages.
*   **`automata_logic.py`**: A specialized handler for deterministic automata operations. It utilizes the `automata-lib` library to perform mathematically precise conversions (e.g., NFA→DFA, Minimization) and uses `graphviz` to generate visual diagrams.

### Configuration & Data
*   **`requirements.txt`**: Lists all Python libraries required to run the project (e.g., `streamlit`, `google-generativeai`, `automata-lib`).
*   **`packages.txt`**: Used by deployment platforms (like Streamlit Cloud) to install system-level dependencies. It lists `graphviz`.
*   **`secrets.toml.example`**: A template file showing how to configure the API key using Streamlit secrets.
*   **`test_inputs.csv`**: A sample CSV file containing a list of strings (e.g., `001`, `111`, `010`). This can be used to demonstrate the "Batch Testing" feature.
