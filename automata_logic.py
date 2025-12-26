from automata.fa.nfa import NFA
from automata.fa.dfa import DFA
from automata.fa.gnfa import GNFA
import graphviz
import pandas as pd
import string

class AutomataHandler:
    @staticmethod
    def _generate_label(index):
        """Generates labels A, B, ..., Z, A1, B1, ..."""
        if index < 26:
            return string.ascii_uppercase[index]
        else:
            return f"{string.ascii_uppercase[index % 26]}{index // 26}"

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
        Returns: (dfa_object, mapping_dict)
        """
        dfa_states = set()
        dfa_transitions = {}
        dfa_final_states = set()

        # The initial state of the DFA is the epsilon-closure of the NFA's initial state
        initial_dfa_state = frozenset(AutomataHandler._get_epsilon_closure(nfa_obj, {nfa_obj.initial_state}))

        # Mapping logic: Discovery order
        mapping = {} # frozenset -> "A"
        state_list_ordered = [initial_dfa_state]
        mapping[initial_dfa_state] = AutomataHandler._generate_label(0)

        unprocessed_states = [initial_dfa_state]
        dfa_states.add(initial_dfa_state)

        while unprocessed_states:
            current_dfa_state_frozenset = unprocessed_states.pop(0)
            current_dfa_state_set = set(current_dfa_state_frozenset)

            # This state is final if any of its NFA states are final
            if not current_dfa_state_set.isdisjoint(nfa_obj.final_states):
                dfa_final_states.add(current_dfa_state_frozenset)

            dfa_transitions[current_dfa_state_frozenset] = {}

            for symbol in sorted(list(nfa_obj.input_symbols)):
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

                # If this is a new DFA state, process it
                if next_dfa_state_frozenset not in dfa_states:
                    dfa_states.add(next_dfa_state_frozenset)
                    unprocessed_states.append(next_dfa_state_frozenset)

                    # Assign next available label
                    new_label = AutomataHandler._generate_label(len(mapping))
                    mapping[next_dfa_state_frozenset] = new_label
                    state_list_ordered.append(next_dfa_state_frozenset)

        # Construct final DFA with Mapped Names (A, B, C...)
        final_dfa_obj_states = set(mapping.values())
        final_dfa_obj_initial_state = mapping[initial_dfa_state]
        final_dfa_obj_final_states = {mapping[fs] for fs in dfa_final_states}
        final_dfa_obj_transitions = {}

        for state, transitions in dfa_transitions.items():
            mapped_state = mapping[state]
            final_dfa_obj_transitions[mapped_state] = {
                symbol: mapping[target] for symbol, target in transitions.items()
            }

        dfa = DFA(
            states=final_dfa_obj_states,
            input_symbols=nfa_obj.input_symbols - {''}, # Remove epsilon from DFA alphabet
            transitions=final_dfa_obj_transitions,
            initial_state=final_dfa_obj_initial_state,
            final_states=final_dfa_obj_final_states,
            allow_partial=True
        )

        return dfa, mapping

    @staticmethod
    def minimize_dfa(dfa_obj):
        return dfa_obj.minify()

    @staticmethod
    def minimize_dfa_with_steps(dfa_obj):
        """
        Minimizes the DFA and returns the equivalence steps (Moore's Algorithm).
        Returns: (minimized_dfa, steps_list, mapping_dict)
        Manual construction of DFA guarantees consistency with the steps shown.
        """
        # 1. Initialize Equivalence 0 (Final and Non-Final)
        states = dfa_obj.states
        final = dfa_obj.final_states
        non_final = states - final
        input_symbols = sorted(list(dfa_obj.input_symbols))

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
                sub_groups = {}
                for state in group:
                    signature = []
                    for symbol in input_symbols:
                        target = dfa_obj.transitions[state].get(symbol)
                        if target is None:
                            signature.append(-1)
                        else:
                            found = False
                            for idx, p in enumerate(partitions):
                                if target in p:
                                    signature.append(idx)
                                    found = True
                                    break
                            if not found:
                                signature.append(-2)
                    signature = tuple(signature)
                    if signature not in sub_groups:
                        sub_groups[signature] = set()
                    sub_groups[signature].add(state)

                for subgroup in sub_groups.values():
                    new_partitions.append(subgroup)

            k += 1
            new_partitions.sort(key=lambda s: min(str(x) for x in s))
            steps.append(f"Equivalence {k}: {new_partitions}")

            if new_partitions == partitions:
                break
            partitions = new_partitions

        # ---------------------------------------------------------------------
        # Construct the new Minimized DFA manually from the final partitions
        # ---------------------------------------------------------------------

        # Mapping Logic: Assign A, B, C... to the resulting partitions
        # We need a consistent order. Let's find the partition containing the start state first.
        # Then BFS order? Or just sorted partition order?
        # The prompt asked for "start with zero trace".
        # We'll use the partition containing initial_state as 'A' (Index 0).
        # Then order the rest consistently.

        partition_list = [frozenset(p) for p in partitions]

        # Find start partition
        start_partition = None
        for p in partition_list:
            if dfa_obj.initial_state in p:
                start_partition = p
                break

        # Create ordered list starting with start_partition
        ordered_partitions = [start_partition]
        remaining = [p for p in partition_list if p != start_partition]
        # Sort remaining to be deterministic (e.g. by smallest element string)
        remaining.sort(key=lambda s: min(str(x) for x in s))
        ordered_partitions.extend(remaining)

        mapping = {}
        for i, p in enumerate(ordered_partitions):
            mapping[p] = AutomataHandler._generate_label(i)

        # Build DFA
        new_states = set(mapping.values())
        new_transitions = {}
        new_start_state = mapping[start_partition]
        new_final_states = set()

        # Helper to find which partition a state belongs to
        def get_partition(s):
            for p in partitions:
                if s in p:
                    return frozenset(p)
            return None

        for p_frozen in ordered_partitions:
            mapped_state = mapping[p_frozen]

            # Determine if Final
            if not p_frozen.isdisjoint(dfa_obj.final_states):
                new_final_states.add(mapped_state)

            # Build Transitions
            rep = next(iter(p_frozen))
            new_transitions[mapped_state] = {}

            for symbol in input_symbols:
                target = dfa_obj.transitions[rep].get(symbol)
                if target is not None:
                    target_partition = get_partition(target)
                    if target_partition:
                        new_transitions[mapped_state][symbol] = mapping[target_partition]

        minimized_dfa = DFA(
            states=new_states,
            input_symbols=set(input_symbols),
            transitions=new_transitions,
            initial_state=new_start_state,
            final_states=new_final_states,
            allow_partial=True
        )

        return minimized_dfa, steps, mapping

    @staticmethod
    def get_dfa_table(dfa_obj):
        """
        Returns a pandas DataFrame representation of the DFA transitions.
        Sorted by BFS order starting from the initial state, followed by unreachable states.
        """
        data = {}
        for state in dfa_obj.states:
            state_label = str(state)
            data[state_label] = {}
            for symbol in dfa_obj.input_symbols:
                target = dfa_obj.transitions[state].get(symbol, "{}")
                data[state_label][symbol] = str(target)

        df = pd.DataFrame.from_dict(data, orient='index')

        # Determine BFS order for rows
        start = dfa_obj.initial_state
        visited = {start}
        queue = [start]
        bfs_order = [start]

        # Sort symbols for deterministic traversal
        sorted_symbols = sorted(list(dfa_obj.input_symbols))

        while queue:
            current = queue.pop(0)
            for symbol in sorted_symbols:
                target = dfa_obj.transitions[current].get(symbol)
                if target is not None and target not in visited:
                    visited.add(target)
                    queue.append(target)
                    bfs_order.append(target)

        # Identify unreachable states and sort them alphabetically
        all_states = dfa_obj.states
        unreachable = list(all_states - visited)
        unreachable.sort(key=lambda s: str(s))

        # Final ordering: BFS reachable + Sorted unreachable
        final_order_objs = bfs_order + unreachable
        final_order_labels = [str(s) for s in final_order_objs]

        # Sort columns (alphabet)
        df = df.reindex(sorted(df.columns), axis=1)

        # Reindex rows based on computed order
        # Only keep labels that actually exist in the dataframe (safety check)
        valid_labels = [lbl for lbl in final_order_labels if lbl in df.index]
        df = df.reindex(valid_labels)

        return df

    @staticmethod
    def regex_to_nfa(regex_str):
        return NFA.from_regex(regex_str)

    @staticmethod
    def regex_to_dfa(regex_str):
        """
        Converts Regex -> NFA -> DFA using custom subset construction.
        Returns: (dfa, mapping)
        """
        nfa = NFA.from_regex(regex_str)
        return AutomataHandler.nfa_to_dfa(nfa)

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
            """Sanitize state label to look cleaner (e.g. remove frozenset(...) or list-style strings)."""
            lbl = str(s)
            # Handle frozenset({...})
            if lbl.startswith("frozenset({") and lbl.endswith("})"):
                return "{" + lbl[11:-2] + "}"
            # Handle list style ['q0', 'q1'] from custom NFA conversion
            if lbl.startswith("['") and lbl.endswith("']"):
                # Remove brackets and quotes
                return "{" + lbl[1:-1].replace("'", "") + "}"
            # Handle empty list style []
            if lbl == "[]":
                return "{}"
            # Handle explicit "{}" string
            if lbl == "{}":
                return "{}"
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
