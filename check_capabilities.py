from automata.fa.nfa import NFA
from automata.fa.dfa import DFA

print("Checking automata-lib capabilities...")

# 1. NFA to DFA
try:
    nfa = NFA(
        states={'q0', 'q1', 'q2'},
        input_symbols={'0', '1'},
        transitions={
            'q0': {'0': {'q0', 'q1'}},
            'q1': {'1': {'q2'}},
            'q2': {}
        },
        initial_state='q0',
        final_states={'q2'}
    )
    dfa = DFA.from_nfa(nfa)
    print("NFA -> DFA: OK")
except Exception as e:
    print(f"NFA -> DFA: Failed ({e})")

# 2. DFA Minimization
try:
    dfa_min = dfa.minify()
    print("DFA Minimization: OK")
except Exception as e:
    print(f"DFA Minimization: Failed ({e})")

# 3. Regex Capabilities
try:
    # Check if from_regex exists in NFA or DFA
    # automata-lib usually uses the 'gnfa' module or similar for regex?
    # Let's check typical methods
    if hasattr(NFA, 'from_regex'):
        print("NFA.from_regex: Exists")
    else:
        print("NFA.from_regex: Does not exist")

    if hasattr(DFA, 'from_regex'):
        print("DFA.from_regex: Exists")

except Exception as e:
    print(f"Regex Check: Failed ({e})")

# 4. DFA/NFA to Regex?
# Usually not direct in basic libs without gnfa
try:
    from automata.fa.gnfa import GNFA
    # dfa to regex often goes via GNFA
    print("GNFA module found, likely supports DFA -> Regex")
except ImportError:
    print("GNFA module not found")
