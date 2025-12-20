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
        # retain_names=True ensures states are frozensets of original states (e.g. {q0, q1})
        # minify=False ensures we see the full powerset construction result before minimization
        return DFA.from_nfa(nfa_obj, retain_names=True, minify=False)

    @staticmethod
    def minimize_dfa(dfa_obj):
        return dfa_obj.minify()

    @staticmethod
    def minimize_dfa_with_steps(dfa_obj):
        """
        Minimizes the DFA and returns the equivalence steps (Moore's Algorithm).
        Returns: (minimized_dfa, steps_list)
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
                # Two states u, v are k+1 equivalent if for all symbols 'a',
                # delta(u, a) and delta(v, a) are in the same k-equivalence group.

                # Map each state to a signature based on which group its transitions land in
                sub_groups = {}
                for state in group:
                    signature = []
                    for symbol in input_symbols:
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

                            if not found:
                                # Target is effectively a dead state not in 'states' set?
                                signature.append(-2)
                    signature = tuple(signature)

                    if signature not in sub_groups:
                        sub_groups[signature] = set()
                    sub_groups[signature].add(state)

                for subgroup in sub_groups.values():
                    new_partitions.append(subgroup)

            k += 1
            # Sort partitions for consistent output representation
            new_partitions.sort(key=lambda s: min(str(x) for x in s))

            steps.append(f"Equivalence {k}: {new_partitions}")

            if new_partitions == partitions:
                break
            partitions = new_partitions

        # ---------------------------------------------------------------------
        # Construct the new Minimized DFA manually from the final partitions
        # ---------------------------------------------------------------------

        # Map old state -> new partition representative (frozenset)
        # We will use the frozenset itself as the state label (key) for the new DFA
        # This preserves the info of which states were merged.

        new_states = set()
        new_transitions = {}
        new_start_state = None
        new_final_states = set()

        # Helper to find which partition a state belongs to
        # (This is O(N) but N is small)
        def get_partition(s):
            for p in partitions:
                if s in p:
                    return frozenset(p)
            return None

        for p in partitions:
            p_frozen = frozenset(p)
            new_states.add(p_frozen)

            # Determine if Start/Final
            # If any state in p is Start, p is Start
            if dfa_obj.initial_state in p:
                new_start_state = p_frozen

            # If any state in p is Final, p is Final (Initial split ensures all are)
            if not p.isdisjoint(dfa_obj.final_states):
                new_final_states.add(p_frozen)

            # Build Transitions
            # Pick a representative state from the partition to determine behavior
            rep = next(iter(p))
            new_transitions[p_frozen] = {}

            for symbol in input_symbols:
                target = dfa_obj.transitions[rep].get(symbol)
                if target is not None:
                    target_partition = get_partition(target)
                    if target_partition:
                        new_transitions[p_frozen][symbol] = target_partition
                    else:
                        # Target maps to something outside partitions (Sink/Dead)
                        # We omit it, keeping it as a partial DFA (implicit sink)
                        pass
                else:
                    # Missing transition
                    pass

        minimized_dfa = DFA(
            states=new_states,
            input_symbols=set(input_symbols),
            transitions=new_transitions,
            initial_state=new_start_state,
            final_states=new_final_states,
            allow_partial=True
        )

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
