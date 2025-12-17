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

print("Checking explicit None check...")
try:
    if dfa is not None:
        print("dfa is not None (Success)")
    else:
        print("dfa is None")
except Exception as e:
    print(f"Check failed: {e}")
