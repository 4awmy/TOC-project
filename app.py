import streamlit as st
import os
import pandas as pd
from logic import LanguageProcessor
from automata_logic import AutomataHandler

# Page Config
st.set_page_config(
    page_title="Automata & Formal Language Studio",
    page_icon="📐",
    layout="wide"
)

# Title
st.title("📐 Automata & Formal Language Studio")

# WARNING: It is generally not safe to hardcode API keys in code.
# Consider using environment variables for production.
DEFAULT_API_KEY = ""

# Sidebar for API Key
with st.sidebar:
    st.header("Settings")

    # Check if key is in env, otherwise use default
    current_key = os.environ.get("GOOGLE_API_KEY", DEFAULT_API_KEY)

    api_key = st.text_input("Google API Key", value=current_key, type="password")

    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key

    st.markdown("---")
    st.markdown("### About")
    st.markdown("This tool uses AI to analyze formal languages and test strings against them.")

# Initialize Session State
if "processor" not in st.session_state:
    st.session_state.processor = LanguageProcessor()

if "history" not in st.session_state:
    st.session_state.history = []

processor = st.session_state.processor

# Main Content
tab1, tab2, tab3 = st.tabs(["Define & Test Language", "Batch Testing", "Automata Operations"])

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

    # Display Current Language Info
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

        st.markdown("---")
        st.subheader("Test Strings")

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

with tab2:
    st.header("Batch Testing")

    if "current_description" not in st.session_state:
        st.warning("Please define a language in the 'Define & Test Language' tab first.")
    else:
        st.write(f"Testing against: **{st.session_state.current_description}**")

        input_method = st.radio("Input Method", ["Manual Entry (CSV format)", "Upload CSV", "Hardcoded Samples"])

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


with tab3:
    st.header("Automata Converter")
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
            target_options = ["NFA"]

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

        st.button("Load Example", on_click=load_example_callback)

    elif source_type == "Regex":
        st.subheader("Define Regex")
        regex_input = st.text_input("Regular Expression", "0*10*")

    st.divider()

    # 3. Action
    if st.button(f"Convert {source_type} -> {target_type}", type="primary"):
        try:
            result_obj = None
            handler = AutomataHandler()

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
                    # Display Table
                    st.subheader("Transition Table (DFA)")
                    st.table(handler.get_dfa_table(result_obj))

                elif target_type == "Regex":
                    # NFA -> DFA -> Regex
                    temp_dfa = handler.nfa_to_dfa(nfa)
                    result_str = handler.dfa_to_regex(temp_dfa)
                    st.success(f"Generated Regex: `{result_str}`")

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
                            # DFA must be complete usually, or we assume trap state?
                            # Automata-lib DFA requires complete transitions usually
                            pass

                dfa = handler.create_dfa(states, alphabet, transitions, start_state, final_states_sel)

                if target_type == "Minimized DFA":
                    result_obj, steps = handler.minimize_dfa_with_steps(dfa)

                    st.subheader("Minimization Steps")
                    for step in steps:
                        st.text(step)

                    st.subheader("Minimized Transition Table")
                    st.table(handler.get_dfa_table(result_obj))

                elif target_type == "Regex":
                    result_str = handler.dfa_to_regex(dfa)
                    st.success(f"Generated Regex: `{result_str}`")

            elif source_type == "Regex":
                if target_type == "NFA":
                    result_obj = handler.regex_to_nfa(regex_input)

            # Display Result Object (if it's an automaton)
            if result_obj is not None:
                st.success("Conversion Successful!")

                # Visualization
                try:
                    dot = handler.get_graphviz_source(result_obj)
                    st.graphviz_chart(dot.source)
                except Exception as e:
                    st.warning(f"Visualization failed: {e}")
                    # Fallback text representation
                    st.text(str(result_obj.transitions))

        except Exception as e:
            st.error(f"Error: {e}")
