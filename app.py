import streamlit as st
import os
import pandas as pd
from logic import LanguageProcessor
from automata_logic import AutomataHandler
from automata.fa.dfa import DFA

# Page Config
st.set_page_config(
    page_title="Automata & Formal Language Studio",
    page_icon="📐",
    layout="wide"
)

# Title
st.title("📐 Automata & Formal Language Studio")

# -----------------------------------------------------------------------------
# API Key Handling & Sidebar
# -----------------------------------------------------------------------------
DEFAULT_API_KEY = ""

with st.sidebar:
    st.header("Settings")

    # Priority: 1. Streamlit Secrets, 2. OS Environment, 3. User Input
    # Try to get key from secrets or env
    system_key = None
    if "GOOGLE_API_KEY" in st.secrets:
        system_key = st.secrets["GOOGLE_API_KEY"]
    elif "GOOGLE_API_KEY" in os.environ:
        system_key = os.environ["GOOGLE_API_KEY"]

    # If a system key is found (via secrets or env), use it SILENTLY.
    # Do NOT show an input field unless the key is missing.
    if system_key:
        api_key = system_key
        # We don't even show the "System API Key Active" message if we want to be totally silent,
        # but the user requested "use it silently and completely hide the manual text input field".
        # Showing a small badge is good UX so they know it works, but I will hide the INPUT field completely.
        st.success("✅ System API Key Active")
    else:
        st.warning("⚠️ No System API Key found")
        api_key = st.text_input("Enter API Key", type="password")

    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key

    st.markdown("---")
    st.markdown("### About")
    st.markdown("This tool uses AI to analyze formal languages and test strings against them.")

# -----------------------------------------------------------------------------
# Session State Initialization
# -----------------------------------------------------------------------------
if "processor" not in st.session_state:
    st.session_state.processor = LanguageProcessor()

if "history" not in st.session_state:
    st.session_state.history = []

processor = st.session_state.processor

# -----------------------------------------------------------------------------
# Main Content Tabs
# -----------------------------------------------------------------------------
tab1, tab2 = st.tabs(["Define & Test Language", "Automata Studio"])

# =============================================================================
# TAB 1: Define & Test Language (Merged with Batch Testing)
# =============================================================================
with tab1:
    st.header("Define a Language")

    col1, col2 = st.columns([2, 1])

    with col1:
        # Input for Language Description
        description = st.text_area(
            "Enter Language Description",
            placeholder="e.g., The set of all strings over {0, 1} that start with 0 and end with 1",
            height=100
        )

        example_lang = st.selectbox(
            "Or select an example:",
            [
                "",
                "The set of all strings over {0, 1} that start with 0 and end with 1",
                "The set of strings with an equal number of a's and b's",
                "Strings representing palindromes over {a, b}",
                "Strings containing the substring '101'",
                "The set of strings matching the email format"
            ]
        )

        if example_lang:
            description = example_lang

    with col2:
        analyze_btn = st.button("Analyze Language", type="primary")

    # Analysis Result
    if analyze_btn and description:
        if not api_key:
            st.error("Please provide a Google API Key in the sidebar.")
        else:
            with st.spinner("Analyzing..."):
                # Force re-init to pick up key if it changed
                processor.ai.configure_api(api_key)

                result = processor.set_language(description)

            if "error" in result:
                st.error(f"Error: {result['error']}")
            else:
                st.success("Language Analyzed!")
                st.session_state.current_result = result
                st.session_state.current_description = description

    # Display Current Language Info & Testing
    if "current_result" in st.session_state:
        result = st.session_state.current_result
        desc = st.session_state.current_description

        st.info(f"**Current Language:** {desc}")

        c1, c2 = st.columns(2)
        with c1:
            if result.get("is_regular"):
                st.success(f"**Type:** Regular Language")
                st.code(result.get("regex"), language="text")
            else:
                st.warning(f"**Type:** Non-Regular Language")

        with c2:
            st.write(f"**Explanation:** {result.get('explanation')}")

        st.divider()
        st.subheader("String Testing")

        test_mode = st.radio("Test Mode", ["Single String", "Batch Test"], horizontal=True)

        if test_mode == "Single String":
            test_str = st.text_input("Enter a string to test")
            if st.button("Check String"):
                if not test_str:
                    st.warning("Enter a string.")
                else:
                    with st.spinner(f"Checking '{test_str}'..."):
                        res = processor.process_string(test_str)

                    if "error" in res:
                        st.error(res["error"])
                    else:
                        accepted = res.get("accepted")
                        reason = res.get("reason")

                        if accepted:
                            st.success(f"✅ ACCEPTED: {test_str}")
                        else:
                            st.error(f"❌ REJECTED: {test_str}")
                        st.write(f"**Reason:** {reason}")

        else: # Batch Testing
            st.markdown("#### Batch Testing Options")
            input_method = st.selectbox("Input Method", ["Manual Entry (CSV format)", "Upload CSV", "Hardcoded Samples"])

            strings_to_test = []

            if input_method == "Manual Entry (CSV format)":
                raw_text = st.text_area("Enter strings (one per line or comma separated)", "001\n111\n010")
                if raw_text:
                    strings_to_test = [s.strip() for s in raw_text.replace(',', '\n').split('\n') if s.strip()]

            elif input_method == "Upload CSV":
                uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
                if uploaded_file is not None:
                    df = pd.read_csv(uploaded_file, header=None)
                    strings_to_test = df[0].astype(str).tolist()

            elif input_method == "Hardcoded Samples":
                strings_to_test = ["001", "111", "010", "101", "00001", "aab", "aba", "abc"]
                st.write(f"Samples: {', '.join(strings_to_test)}")

            if st.button("Run Batch Test"):
                if not strings_to_test:
                    st.warning("No strings provided.")
                else:
                    results = []
                    progress_bar = st.progress(0)

                    for i, s in enumerate(strings_to_test):
                        res = processor.process_string(s)
                        results.append({
                            "String": s,
                            "Status": "ACCEPTED" if res.get("accepted") else "REJECTED",
                            "Reason": res.get("reason", "")
                        })
                        progress_bar.progress((i + 1) / len(strings_to_test))

                    st.table(pd.DataFrame(results))

# =============================================================================
# TAB 2: Automata Studio (NFA, DFA, Regex Ops)
# =============================================================================
with tab2:
    st.header("Automata Studio")
    st.markdown("Convert between NFA, DFA, and Regex using deterministic algorithms.")

    # 1. Converter Selection
    c1, c2 = st.columns(2)
    with c1:
        source_type = st.selectbox("From", ["NFA", "DFA", "Regex"])
    with c2:
        # Dynamic options based on source
        if source_type == "NFA":
            target_options = ["DFA", "Regex"]
        elif source_type == "DFA":
            target_options = ["Regex", "Minimized DFA"]
        elif source_type == "Regex":
            target_options = ["NFA", "DFA"]

        target_type = st.selectbox("To", target_options)

    st.divider()

    # 2. Input Section
    if source_type in ["NFA", "DFA"]:
        st.subheader(f"Define {source_type}")

        # State & Alphabet Config
        col_conf1, col_conf2 = st.columns(2)
        with col_conf1:
            # Initialize default values in session state if not present
            if "states_input" not in st.session_state:
                st.session_state.states_input = "q0, q1, q2"
            if "alphabet_input" not in st.session_state:
                st.session_state.alphabet_input = "0, 1"

            states_str = st.text_input("States (comma separated)", key="states_input")
            alphabet_str = st.text_input("Alphabet (comma separated)", key="alphabet_input")

        states = [s.strip() for s in states_str.split(",") if s.strip()]
        alphabet = [s.strip() for s in alphabet_str.split(",") if s.strip()]

        with col_conf2:
            start_state = st.selectbox("Start State", states)
            final_states_sel = st.multiselect("Final States", states)

        # Transition Table Editor
        st.markdown("### Transition Table")
        st.caption("For NFA, enter multiple states separated by commas (e.g. 'q0, q1'). Use '{}' for empty.")

        # Initialize dataframe for transitions
        # Rows = States, Cols = Alphabet
        if "trans_df" not in st.session_state:
             st.session_state.trans_df = pd.DataFrame("", index=states, columns=alphabet)
        else:
            # Update index/cols if changed
            if not st.session_state.trans_df.index.equals(pd.Index(states)) or \
               not st.session_state.trans_df.columns.equals(pd.Index(alphabet)):
                st.session_state.trans_df = pd.DataFrame("", index=states, columns=alphabet)

        edited_df = st.data_editor(st.session_state.trans_df, use_container_width=True)

        # Load Example Button
        def load_example_callback():
            if source_type == "NFA":
                # Example: Infinite NFA (0-9)
                example_states = [str(i) for i in range(10)]
                example_alphabet = ["0", "1"]

                # Helper to format set of states for the table (comma separated)
                def fmt(s): return ", ".join(sorted(list(s))) if s else ""

                data = {
                    "0": [fmt({'1', '2'}), fmt({'6', '7'})],
                    "1": [fmt({'1', '3'}), fmt({'2'})],
                    "2": [fmt({'6', '7'}), fmt({'3'})],
                    "3": [fmt({'8', '9'}), fmt({'1'})],
                    "4": [fmt({'5', '6'}), fmt({'0'})],
                    "5": [fmt({'7', '8'}), fmt({'0'})],
                    "6": [fmt({'4'}),      fmt({'6'})],
                    "7": [fmt({'5'}),      fmt({'1'})],
                    "8": [fmt({'4', '7'}), fmt({'3'})],
                    "9": [fmt({'1', '6'}), fmt({'1'})]
                }

                st.session_state.states_input = ", ".join(example_states)
                st.session_state.alphabet_input = ", ".join(example_alphabet)
                st.session_state.trans_df = pd.DataFrame.from_dict(data, orient='index', columns=example_alphabet)

            elif source_type == "DFA":
                # Check target type to load appropriate example
                if target_type == "Minimized DFA":
                    # Example: Complex 8-state DFA for minimization (Standard Moore's Alg Example)
                    ex_states = ["A", "B", "C", "D", "E", "F", "G", "H"]
                    ex_alphabet = ["0", "1"]

                    # C is Final state (typical textbook example)
                    # Start state A
                    data = {
                        "A": ["B", "F"],
                        "B": ["G", "C"],
                        "C": ["A", "C"],
                        "D": ["C", "G"],
                        "E": ["H", "F"],
                        "F": ["C", "G"],
                        "G": ["G", "E"],
                        "H": ["G", "C"]
                    }
                    st.session_state.states_input = ", ".join(ex_states)
                    st.session_state.alphabet_input = ", ".join(ex_alphabet)
                    st.session_state.trans_df = pd.DataFrame.from_dict(data, orient='index', columns=ex_alphabet)

                else:
                    # Example: Simple 2-state DFA for Regex conversion (Arden's Theorem Example)
                    # A -> 0:A, 1:B
                    # B -> 0:B, 1:A
                    # A is start, B is final
                    ex_states = ["A", "B"]
                    ex_alphabet = ["0", "1"]

                    data = {
                        "A": ["A", "B"],
                        "B": ["B", "A"]
                    }

                    st.session_state.states_input = ", ".join(ex_states)
                    st.session_state.alphabet_input = ", ".join(ex_alphabet)
                    st.session_state.trans_df = pd.DataFrame.from_dict(data, orient='index', columns=ex_alphabet)

            elif source_type == "Regex":
                 st.session_state.regex_input_field = "(a|b)*abb"

        st.button(f"Load {source_type} Example", on_click=load_example_callback)

    elif source_type == "Regex":
        st.subheader("Define Regex")
        # Initialize session state for regex if not present
        if "regex_input_field" not in st.session_state:
             st.session_state.regex_input_field = "0*10*"

        regex_input = st.text_input("Regular Expression", key="regex_input_field")

        # Load Example Button for Regex
        def load_regex_example():
             st.session_state.regex_input_field = "(a|b)*abb"

        st.button("Load Regex Example", on_click=load_regex_example)

    st.divider()

    # 3. Action
    if st.button(f"Convert {source_type} -> {target_type}", type="primary"):
        try:
            handler = AutomataHandler()

            # Clear previous results
            if "automata_result" in st.session_state:
                del st.session_state["automata_result"]
            if "automata_regex" in st.session_state:
                del st.session_state["automata_regex"]
            if "automata_steps" in st.session_state:
                del st.session_state["automata_steps"]

            if source_type == "NFA":
                # Parse Table to Transitions Dict
                transitions = {}
                for state in states:
                    transitions[state] = {}
                    for symbol in alphabet:
                        target_str = edited_df.loc[state, symbol]
                        if target_str.strip() and target_str != "{}":
                            targets = {t.strip() for t in target_str.split(',')}
                            transitions[state][symbol] = targets
                        else:
                             transitions[state][symbol] = set() # Empty set

                nfa = handler.create_nfa(states, alphabet, transitions, start_state, final_states_sel)

                if target_type == "DFA":
                    result_obj = handler.nfa_to_dfa(nfa)
                    st.session_state["automata_result"] = result_obj

                elif target_type == "Regex":
                    # NFA -> DFA -> Regex
                    temp_dfa = handler.nfa_to_dfa(nfa)
                    result_str = handler.dfa_to_regex(temp_dfa)
                    st.session_state["automata_regex"] = result_str

            elif source_type == "DFA":
                # Parse Table
                transitions = {}
                for state in states:
                    transitions[state] = {}
                    for symbol in alphabet:
                        target = edited_df.loc[state, symbol]
                        if target.strip():
                             transitions[state][symbol] = target.strip()
                        else:
                            pass

                dfa = handler.create_dfa(states, alphabet, transitions, start_state, final_states_sel)

                if target_type == "Minimized DFA":
                    result_obj, steps = handler.minimize_dfa_with_steps(dfa)
                    st.session_state["automata_result"] = result_obj
                    st.session_state["automata_steps"] = steps

                elif target_type == "Regex":
                    result_str = handler.dfa_to_regex(dfa)
                    st.session_state["automata_regex"] = result_str

            elif source_type == "Regex":
                if target_type == "NFA":
                    result_obj = handler.regex_to_nfa(regex_input)
                    st.session_state["automata_result"] = result_obj
                elif target_type == "DFA":
                    result_obj = handler.regex_to_dfa(regex_input)
                    st.session_state["automata_result"] = result_obj

        except Exception as e:
            st.error(f"Error: {e}")

    # Display Results (Persistent)
    if "automata_regex" in st.session_state:
        st.success(f"Generated Regex: `{st.session_state['automata_regex']}`")

    if st.session_state.get("automata_steps"):
        st.subheader("Minimization Steps")
        for step in st.session_state["automata_steps"]:
            st.text(step)

    # Check for result object safely (explicit None check to avoid InfiniteLanguageException)
    if st.session_state.get("automata_result") is not None:
        result_obj = st.session_state["automata_result"]

        st.success("Operation Successful!")

        # Display Table if it's a DFA/NFA
        # Note: We can infer type or just try to display table if it has 'states'
        handler = AutomataHandler()
        try:
            # If it has transitions, we can show a table
            if hasattr(result_obj, 'transitions'):
                st.subheader("Transition Table")
                st.table(handler.get_dfa_table(result_obj))
        except:
            pass # Might be NFA or other format where get_dfa_table isn't perfect, or just skip

        # Visualization
        try:
            dot = handler.get_graphviz_source(result_obj)
            st.graphviz_chart(dot.source)
        except Exception as e:
            st.warning(f"Visualization failed: {e}")
            # Fallback
            if hasattr(result_obj, 'transitions'):
                st.text(str(result_obj.transitions))

        # Add Chainable Minimization Option (Merged from main branch ideas, but using safe variables)
        if isinstance(result_obj, DFA):
            st.divider()
            st.markdown("### DFA Operations")

            op_col1, op_col2 = st.columns(2)

            with op_col1:
                if st.button("Minimize this DFA", type="primary"):
                    try:
                        with st.spinner("Minimizing..."):
                            minimized_dfa, steps = handler.minimize_dfa_with_steps(result_obj)

                            # Store result to persist
                            st.session_state["automata_result"] = minimized_dfa
                            st.session_state["automata_steps"] = steps
                            st.rerun() # Rerun to update the display with minimized version
                    except Exception as e:
                        st.error(f"Minimization failed: {e}")

            with op_col2:
                if st.button("Convert to Regex"):
                    try:
                        with st.spinner("Converting..."):
                            regex_result = handler.dfa_to_regex(result_obj)
                            st.session_state["automata_regex"] = regex_result
                            st.rerun()
                    except Exception as e:
                        st.error(f"Conversion failed: {e}")
