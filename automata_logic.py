from automata.fa.nfa import NFA
from automata.fa.dfa import DFA
from automata.fa.gnfa import GNFA
import graphviz

class AutomataHandler:
    @staticmethod
    def create_nfa(states, alphabet, transitions, start_state, final_states):
        """
        Creates an NFA object.
        transitions: dict {state: {symbol: {target_states}}}
        """
        return NFA(
            states=set(states),
            input_symbols=set(alphabet),
            transitions=transitions,
            initial_state=start_state,
            final_states=set(final_states)
        )

    @staticmethod
    def create_dfa(states, alphabet, transitions, start_state, final_states):
        """
        Creates a DFA object.
        transitions: dict {state: {symbol: target_state}}
        """
        return DFA(
            states=set(states),
            input_symbols=set(alphabet),
            transitions=transitions,
            initial_state=start_state,
            final_states=set(final_states)
        )

    @staticmethod
    def nfa_to_dfa(nfa_obj):
        return DFA.from_nfa(nfa_obj)

    @staticmethod
    def minimize_dfa(dfa_obj):
        return dfa_obj.minify()

    @staticmethod
    def regex_to_nfa(regex_str):
        return NFA.from_regex(regex_str)

    @staticmethod
    def dfa_to_regex(dfa_obj):
        gnfa = GNFA.from_dfa(dfa_obj)
        return gnfa.to_regex()

    @staticmethod
    def get_graphviz_source(automaton):
        """
        Manually constructs a graphviz.Digraph object from the automaton.
        This avoids dependency on pygraphviz/coloraide required by automaton.show_diagram().
        """
        dot = graphviz.Digraph()
        dot.attr(rankdir='LR')

        # Add states
        for state in automaton.states:
            shape = 'doublecircle' if state in automaton.final_states else 'circle'
            # Convert state to string safely (dfa states can be sets/tuples)
            state_label = str(state)

            # Start state indication
            if state == automaton.initial_state:
                dot.node('start', shape='point')
                dot.edge('start', state_label)

            dot.node(state_label, shape=shape)

        # Add transitions
        # NFA transitions: {state: {symbol: {targets}}}
        # DFA transitions: {state: {symbol: target}}
        for src, transitions in automaton.transitions.items():
            src_label = str(src)
            for symbol, target in transitions.items():
                if isinstance(target, set): # NFA
                    for t in target:
                        dot.edge(src_label, str(t), label=symbol)
                else: # DFA
                    dot.edge(src_label, str(target), label=symbol)

        return dot
