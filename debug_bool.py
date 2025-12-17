from automata.fa.nfa import NFA
from automata.fa.dfa import DFA

nfa = NFA(
    states={'q0'},
    input_symbols={'0'},
    transitions={'q0': {'0': {'q0'}}},
    initial_state='q0',
    final_states={'q0'}
)

dfa = DFA.from_nfa(nfa)

print("Checking bool(dfa)...")
try:
    if dfa:
        print("dfa is True")
    else:
        print("dfa is False")
except Exception as e:
    print(f"bool(dfa) failed: {e}")
