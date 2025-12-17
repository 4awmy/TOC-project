from automata.fa.nfa import NFA
from automata.fa.dfa import DFA

# Infinite NFA
nfa = NFA(
    states={'q0'},
    input_symbols={'0'},
    transitions={'q0': {'0': {'q0'}}},
    initial_state='q0',
    final_states={'q0'}
)

dfa = DFA.from_nfa(nfa)

print("Checking len(dfa)...")
try:
    print(len(dfa))
except Exception as e:
    print(f"len(dfa) failed: {e}")

print("Checking dfa.cardinality()...")
try:
    print(dfa.cardinality())
except Exception as e:
    print(f"dfa.cardinality() failed: {e}")
