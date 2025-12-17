import streamlit as st
import os
import pandas as pd
from logic import LanguageProcessor

# Page Config
st.set_page_config(
    page_title="Theory of Computation AI",
    page_icon="🤖",
    layout="wide"
)

# Title
st.title("🤖 Theory of Computation AI Tool")

# Sidebar for API Key
with st.sidebar:
    st.header("Settings")

    # Check if key is in env
    env_key = os.environ.get("GOOGLE_API_KEY", "")

    api_key = st.text_input("Google API Key", value=env_key, type="password")

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
tab1, tab2 = st.tabs(["Define & Test Language", "Batch Testing"])

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
