from automata.fa.nfa import NFA
from automata.fa.dfa import DFA
from automata.fa.gnfa import GNFA
import graphviz
import pandas as pd

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
    def minimize_dfa_with_steps(dfa_obj):
        """
        Minimizes the DFA and returns the equivalence steps (Moore's Algorithm).
        Returns: (minimized_dfa, steps_list)
        """
        # 1. Initialize Equivalence 0 (Final and Non-Final)
        states = dfa_obj.states
        final = dfa_obj.final_states
        non_final = states - final

        # P0
        partitions = []
        if non_final: partitions.append(non_final)
        if final: partitions.append(final)

        steps = []
        steps.append(f"Equivalence 0: {partitions}")

        k = 0
        while True:
            new_partitions = []
            for group in partitions:
                if len(group) <= 1:
                    new_partitions.append(group)
                    continue

                # Check consistency within the group
                # Two states u, v are k+1 equivalent if for all symbols 'a',
                # delta(u, a) and delta(v, a) are in the same k-equivalence group.

                # Map each state to a signature based on which group its transitions land in
                sub_groups = {}
                for state in group:
                    signature = []
                    for symbol in sorted(list(dfa_obj.input_symbols)):
                        # Handle partial DFAs (missing transitions go to sink)
                        target = dfa_obj.transitions[state].get(symbol)

                        if target is None:
                            # Use -1 to represent implicit sink state
                            signature.append(-1)
                        else:
                            # Find which partition index this target belongs to
                            found = False
                            for idx, p in enumerate(partitions):
                                if target in p:
                                    signature.append(idx)
                                    found = True
                                    break
                            # If target is not in any partition (should not happen for valid states,
                            # but possible if target is a dead state not in states list?)
                            # Implicitly, all states in DFA should be in one of the partitions.
                            if not found:
                                signature.append(-2) # Error or external state
                    signature = tuple(signature)

                    if signature not in sub_groups:
                        sub_groups[signature] = set()
                    sub_groups[signature].add(state)

                for subgroup in sub_groups.values():
                    new_partitions.append(subgroup)

            k += 1
            # Sort partitions for consistent output representation
            new_partitions.sort(key=lambda s: min(str(x) for x in s)) # Simple sort stability

            steps.append(f"Equivalence {k}: {new_partitions}")

            if new_partitions == partitions:
                break
            partitions = new_partitions

        minimized_dfa = dfa_obj.minify()
        return minimized_dfa, steps

    @staticmethod
    def get_dfa_table(dfa_obj):
        """
        Returns a pandas DataFrame representation of the DFA transitions.
        """
        data = {}
        for state in dfa_obj.states:
            state_label = str(state)
            data[state_label] = {}
            for symbol in dfa_obj.input_symbols:
                target = dfa_obj.transitions[state].get(symbol, "{}")
                data[state_label][symbol] = str(target)

        df = pd.DataFrame.from_dict(data, orient='index')
        # Sort columns (alphabet) and rows (states) for neatness
        df = df.reindex(sorted(df.columns), axis=1)
        df = df.sort_index()
        return df

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

        def safe_label(s):
            """Sanitize state label to look cleaner (e.g. remove frozenset(...))."""
            lbl = str(s)
            if lbl.startswith("frozenset({") and lbl.endswith("})"):
                return "{" + lbl[11:-2] + "}"
            return lbl

        # Add states
        for state in automaton.states:
            shape = 'doublecircle' if state in automaton.final_states else 'circle'
            # Convert state to string safely (dfa states can be sets/tuples)
            state_label = safe_label(state)

            # Start state indication
            if state == automaton.initial_state:
                dot.node('start', shape='point')
                dot.edge('start', state_label)

            dot.node(state_label, shape=shape)

        # Add transitions
        # NFA transitions: {state: {symbol: {targets}}}
        # DFA transitions: {state: {symbol: target}}
        for src, transitions in automaton.transitions.items():
            src_label = safe_label(src)
            for symbol, target in transitions.items():
                if isinstance(target, set): # NFA
                    for t in target:
                        dot.edge(src_label, safe_label(t), label=symbol)
                else: # DFA
                    dot.edge(src_label, safe_label(target), label=symbol)

        return dot
