from automata.fa.nfa import NFA
from automata.fa.dfa import DFA

# Define an infinite NFA (accepts '0' loop)
nfa = NFA(
    states={'q0'},
    input_symbols={'0'},
    transitions={
        'q0': {'0': {'q0'}}
    },
    initial_state='q0',
    final_states={'q0'}
)

print("Creating DFA...")
dfa = DFA.from_nfa(nfa)
print(f"DFA Finite? {dfa.isfinite()}")

print("Attempting show_diagram()...")
try:
    dfa.show_diagram()
    print("show_diagram() success")
except Exception as e:
    print(f"show_diagram() failed: {e}")

print("Attempting str(dfa)...")
try:
    print(str(dfa))
    print("str(dfa) success")
except Exception as e:
    print(f"str(dfa) failed: {e}")
