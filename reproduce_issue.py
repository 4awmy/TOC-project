from automata.fa.nfa import NFA
from automata.fa.dfa import DFA
from automata.fa.gnfa import GNFA

# Define NFA from screenshot
# States: 0-9
# Alphabet: 0, 1
# Start: 0
# Final: 3, 5, 8, 7

nfa = NFA(
    states={'0', '1', '2', '3', '4', '5', '6', '7', '8', '9'},
    input_symbols={'0', '1'},
    transitions={
        '0': {'0': {'1', '2'}, '1': {'6', '7'}},
        '1': {'0': {'1', '3'}, '1': {'2'}},
        '2': {'0': {'6', '7'}, '1': {'3'}},
        '3': {'0': {'8', '9'}, '1': {'1'}},
        '4': {'0': {'5', '6'}, '1': {'0'}},
        '5': {'0': {'7', '8'}, '1': {'0'}},
        '6': {'0': {'4'},      '1': {'6'}},
        '7': {'0': {'5'},      '1': {'1'}},
        '8': {'0': {'4', '7'}, '1': {'3'}},
        '9': {'0': {'1', '6'}, '1': {'1'}}
    },
    initial_state='0',
    final_states={'3', '5', '8', '7'}
)

print("NFA created.")

try:
    dfa = DFA.from_nfa(nfa)
    print(f"DFA created. States: {len(dfa.states)}")
except Exception as e:
    print(f"DFA conversion failed: {e}")
    exit(1)

# Check if language is infinite
try:
    is_finite = dfa.isfinite()
    print(f"Is Finite: {is_finite}")
except Exception as e:
    print(f"Finite check failed: {e}")

# Convert to Regex
try:
    gnfa = GNFA.from_dfa(dfa)
    regex = gnfa.to_regex()
    print(f"Regex length: {len(regex)}")
    print(f"Regex snippet: {regex[:100]}...")
except Exception as e:
    print(f"Regex conversion failed: {e}")
