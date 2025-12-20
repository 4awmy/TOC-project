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
    *   **Powerset Construction (NFA $\to$ DFA)**: The algorithm used to convert an NFA into a DFA by creating states that represent sets of NFA states.
    *   **Kleene's Theorem**: Implementation of conversions between Regular Expressions and Finite Automata.
*   **DFA Minimization (Moore's Algorithm)**:
    *   The project implements an $O(n^2)$ algorithm to minimize DFAs by finding groups of equivalent states.
    *   It iteratively refines partitions (0-equivalence, 1-equivalence, etc.) until no further splitting is possible.

---

## Detailed File Architecture & Logic

### 1. `app.py` (The Frontend & Controller)
**Role:** The entry point and main controller of the application.
*   **Logic:**
    *   **Session State Management**: Uses `st.session_state` to persist data (automata objects, analysis results) across browser reruns. This is crucial because Streamlit re-executes the script on every interaction.
    *   **Tab-Based Navigation**: Separates the workflow into "Define & Test" (AI + Batch) and "Automata Studio" (Structural Operations).
    *   **API Key Handling**: Implements a priority system (`st.secrets` > `os.environ` > User Input) to securely load the Google Gemini Key.
    *   **Error Handling**: Wraps complex operations in `try-except` blocks to prevent crashes from invalid user inputs (e.g., malformed Regex).

### 2. `automata_logic.py` (The Mathematical Engine)
**Role:** Handles all deterministic operations and visualization.
*   **Logic:**
    *   **`create_nfa` / `create_dfa`**: Helper factories that instantiate library objects from the UI's transition table data.
    *   **`minimize_dfa_with_steps`**: A custom implementation of **Moore's Algorithm**.
        *   It starts by partitioning states into Final and Non-Final sets ($P_0$).
        *   In each step $k$, it splits partitions based on whether transitions lead to different partitions in $P_{k-1}$.
        *   It returns the step-by-step logs specifically requested for educational purposes.
    *   **`get_graphviz_source`**: A custom visualization engine.
        *   *Why custom?* The default library `show_diagram` relies on C-dependencies that often fail in cloud environments.
        *   *Sanitization*: It specifically handles the messy output of NFA-to-DFA conversions (where states are `frozenset({'q0', 'q1'})`) and converts them to clean strings (`{q0,q1}`).
        *   *Partial DFAs*: It gracefully handles missing transitions (implicit sink states) to prevent crashes.

### 3. `ai_handler.py` (The AI Integration)
**Role:** Manages communication with Google's Gemini API.
*   **Logic:**
    *   **Prompt Engineering**: Constructs a specific system prompt that forces the AI to respond in JSON format.
    *   **Context Injection**: "You are a Theory of Computation expert..." ensures the AI uses precise terminology.
    *   **Lazy Configuration**: The `configure_api` method allows the API key to be set at runtime (via the UI) rather than requiring it at startup.

### 4. `logic.py` (Business Logic / Orchestration)
**Role:** The bridge between the UI and the AI Handler.
*   **Logic:**
    *   **`LanguageProcessor`**: A class that encapsulates the state of the "current language".
    *   **Orchestration**: It takes the raw string from the UI, sends it to `AIHandler`, validates the JSON response, and stores the resulting Regex/Explanation for use in testing.
    *   **Regex Validation**: It uses Python's `re` module to test strings against the AI-generated regex to provide deterministic "Accepted/Rejected" results.

### 5. Configuration Files
*   **`.streamlit/secrets.toml`**: Stores sensitive data (API Keys). This file is git-ignored to prevent leaks.
*   **`requirements.txt`**: Lists Python packages (`automata-lib`, `streamlit`, `google-generativeai`).
*   **`packages.txt`**: Lists system-level binaries (`graphviz`) required by the deployment environment (e.g., Streamlit Cloud).
*   **`main.py`**: The legacy CLI version of the tool, kept for reference or headless usage.

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
