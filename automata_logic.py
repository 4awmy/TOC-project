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
    def _get_epsilon_closure(nfa_obj, states):
        """
        Computes the epsilon-closure for a set of NFA states.
        This includes the initial states and all states reachable via epsilon transitions.
        """
        closure = set(states)
        stack = list(states)

        while stack:
            current_state = stack.pop()
            # Epsilon transitions are typically denoted by an empty string ''
            epsilon_moves = nfa_obj.transitions.get(current_state, {}).get('', set())

            for next_state in epsilon_moves:
                if next_state not in closure:
                    closure.add(next_state)
                    stack.append(next_state)
        return closure

    @staticmethod
    def nfa_to_dfa(nfa_obj):
        """
        Converts an NFA to a DFA using the Subset Construction Algorithm.
        """
        dfa_states = set()
        dfa_transitions = {}
        dfa_final_states = set()

        # The initial state of the DFA is the epsilon-closure of the NFA's initial state
        initial_dfa_state = frozenset(AutomataHandler._get_epsilon_closure(nfa_obj, {nfa_obj.initial_state}))
        dfa_initial_state = initial_dfa_state

        unprocessed_states = [initial_dfa_state]
        dfa_states.add(initial_dfa_state)

        while unprocessed_states:
            current_dfa_state_frozenset = unprocessed_states.pop(0)
            current_dfa_state_set = set(current_dfa_state_frozenset)

            # This state is final if any of its NFA states are final
            if not current_dfa_state_set.isdisjoint(nfa_obj.final_states):
                dfa_final_states.add(current_dfa_state_frozenset)

            dfa_transitions[current_dfa_state_frozenset] = {}

            for symbol in nfa_obj.input_symbols:
                # Epsilon transitions are not part of the DFA's alphabet
                if symbol == '':
                    continue

                next_nfa_states = set()
                # 1. Find all possible next states from the current set of NFA states
                for nfa_state in current_dfa_state_set:
                    next_nfa_states.update(nfa_obj.transitions.get(nfa_state, {}).get(symbol, set()))

                # 2. Compute the epsilon-closure of this new set of states
                next_dfa_state_set = AutomataHandler._get_epsilon_closure(nfa_obj, next_nfa_states)

                next_dfa_state_frozenset = frozenset(next_dfa_state_set)

                # Add the transition to the DFA
                dfa_transitions[current_dfa_state_frozenset][symbol] = next_dfa_state_frozenset

                # If this is a new DFA state, add it to our list to be processed
                if next_dfa_state_frozenset not in dfa_states:
                    dfa_states.add(next_dfa_state_frozenset)
                    unprocessed_states.append(next_dfa_state_frozenset)

        # The library expects state names to be strings for the DFA constructor,
        # but the logic requires sets for processing. We'll convert the frozensets
        # to a consistent, readable string representation for the final object.
        state_map = {fs: str(sorted(list(fs))) if fs else "{}" for fs in dfa_states}

        final_dfa_obj_states = set(state_map.values())
        final_dfa_obj_initial_state = state_map[dfa_initial_state]
        final_dfa_obj_final_states = {state_map[fs] for fs in dfa_final_states}
        final_dfa_obj_transitions = {}

        for state, transitions in dfa_transitions.items():
            final_dfa_obj_transitions[state_map[state]] = {
                symbol: state_map[target] for symbol, target in transitions.items()
            }

        return DFA(
            states=final_dfa_obj_states,
            input_symbols=nfa_obj.input_symbols - {''}, # Remove epsilon from DFA alphabet
            transitions=final_dfa_obj_transitions,
            initial_state=final_dfa_obj_initial_state,
            final_states=final_dfa_obj_final_states
        )

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
                        target = dfa_obj.transitions[state][symbol]
                        # Find which partition index this target belongs to
                        for idx, p in enumerate(partitions):
                            if target in p:
                                signature.append(idx)
                                break
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
