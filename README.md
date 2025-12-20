# Automata & Formal Language Studio

A powerful AI-powered tool for exploring Theory of Computation concepts, including Regular Languages, Automata, and Regex. This project bridges the gap between abstract formal language theory and practical visualization using modern web technologies and Generative AI.

## Technologies & Concepts Used

### Core Technologies
*   **Python 3.8+**: The primary programming language.
*   **Streamlit**: A react-like framework for building data-driven web apps in pure Python. Used for the entire frontend and state management.
*   **Automata-lib**: A Python library for simulating and converting finite automata (DFA, NFA) and Regular Expressions.
*   **Google Gemini API (Generative AI)**: Used for the "Language Definition" feature, allowing the system to understand natural language descriptions (e.g., "Strings ending in 101") and convert them to formal Regex.
*   **Graphviz**: An open-source graph visualization software. Used here to render state transition diagrams.
*   **Pandas**: Used for handling transition tables (DataFrames) and batch testing results.

### Theoretical Concepts
*   **Finite Automata (FA)**:
    *   **DFA (Deterministic Finite Automata)**: Every state has exactly one transition for each symbol.
    *   **NFA (Non-Deterministic Finite Automata)**: States can have zero, one, or multiple transitions for a symbol, including $\epsilon$-transitions.
*   **Automata Conversions**:
    *   **Subset Construction Algorithm (NFA $\to$ DFA)**:
        *   The project implements a **manual subset construction** algorithm.
        *   It computes the **epsilon-closure** for each state.
        *   It tracks new states as sets of NFA states (e.g., `{q0, q1}`) to explicitly show how the DFA is built.
    *   **Kleene's Theorem**: Implementation of conversions between Regular Expressions and Finite Automata.
*   **DFA Minimization (Moore's Algorithm)**:
    *   The project implements an $O(n^2)$ algorithm to minimize DFAs by finding groups of equivalent states.
    *   It iteratively refines partitions (0-equivalence, 1-equivalence, etc.) until no further splitting is possible.

---

## Detailed File Architecture & Logic

### 1. `app.py` (The Frontend & Controller)
**Role:** The entry point and main controller of the application.
*   **Logic:**
    *   **Session State Management**: Uses `st.session_state` to persist data (automata objects, analysis results, step logs) across browser reruns. This ensures the user's workflow is preserved during interaction.
    *   **Tab-Based Layout**: Organizes the UI into "Define & Test Language" (AI + Batch Testing) and "Automata Studio" (Structural Operations).
    *   **System API Key**: Implements a secure priority system (`st.secrets` > `os.environ` > User Input) to load the Google API Key.
    *   **Robust Error Handling**: Prevents crashes (e.g., `InfiniteLanguageException`) by using explicit state checks instead of implicit boolean evaluations.

### 2. `automata_logic.py` (The Mathematical Engine)
**Role:** Handles all deterministic operations and visualization. This file contains the core algorithmic implementations.
*   **Logic:**
    *   **`nfa_to_dfa` (Manual Subset Construction)**:
        *   Instead of using the library's default conversion (which renames states to integers), this function manually implements the **Powerset Construction** algorithm.
        *   It calculates the epsilon-closure of states and iteratively finds reachable subsets.
        *   **Goal:** To preserve the educational value by showing states labeled as `{q0, q1}`.
    *   **`minimize_dfa_with_steps` (Moore's Algorithm)**:
        *   Implements **Moore's Algorithm** for DFA minimization.
        *   Iteratively calculates $k$-equivalence partitions (0-equiv, 1-equiv...) and logs each step for the user.
        *   **Partial DFA Support**: Constructs the final DFA with `allow_partial=True` to handle cases where transitions are missing (implicit dead states), avoiding validation errors without adding confusing "Sink" states to the diagram.
    *   **`get_graphviz_source` (Custom Visualization)**:
        *   A custom rendering engine that generates DOT source code directly.
        *   **Sanitization**: Detects complex state labels (like `frozenset({'q0', 'q1'})` or `['q0', 'q1']`) and converts them into clean set notation (`{q0, q1}`).
        *   Avoids heavy dependencies like `pygraphviz`, ensuring compatibility with Streamlit Cloud.

### 3. `ai_handler.py` (The AI Integration)
**Role:** Manages communication with Google's Gemini API.
*   **Logic:**
    *   **Prompt Engineering**: Constructs a specific system prompt that forces the AI to respond in JSON format, ensuring predictable parsing.
    *   **Context Injection**: "You are a Theory of Computation expert..." ensures the AI uses precise terminology and focuses on Formal Languages.
    *   **Lazy Configuration**: The `configure_api` method allows the API key to be set at runtime (via the UI) rather than requiring it at startup.

### 4. `logic.py` (Business Logic / Orchestration)
**Role:** The bridge between the UI and the AI Handler.
*   **Logic:**
    *   **`LanguageProcessor`**: A class that encapsulates the state of the "current language".
    *   **Orchestration**: It takes the raw string from the UI, sends it to `AIHandler`, validates the JSON response, and stores the resulting Regex/Explanation for use in testing.
    *   **Regex Validation**: It uses Python's `re` module to test strings against the AI-generated regex to provide deterministic "Accepted/Rejected" results.

### 5. Configuration & Data Files
*   **`.streamlit/secrets.toml`**: Stores sensitive data (API Keys). This file is git-ignored to prevent leaks.
*   **`.streamlit/config.toml`**: Configures Streamlit server settings (e.g., headless mode).
*   **`secrets.toml.example`**: A template file showing users how to configure their own API keys.
*   **`requirements.txt`**: Lists Python packages (`automata-lib`, `streamlit`, `google-generativeai`).
*   **`packages.txt`**: Lists system-level binaries (`graphviz`) required by the deployment environment.
*   **`main.py`**: The legacy CLI version of the tool.
*   **`test_inputs.csv`**: Sample data for the Batch Testing feature.

---

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

The application requires a **Google Gemini API Key** for the "Language Definition" features.

### 1. Streamlit Secrets (Recommended)
1.  Create a folder `.streamlit` in the root.
2.  Create `secrets.toml`:
    ```toml
    GOOGLE_API_KEY = "your_key_here"
    ```

### 2. Sidebar Input
If no system key is found, the app will prompt you to enter one in the sidebar.
