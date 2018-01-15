# coding=utf-8
from enum import IntEnum
import pprint

class FiniteAutomat:
    class MatchMode(IntEnum):
        MATCH_WHOLE = 1
        MATCH_SUB = 2

    def __init__(self):
        self._graph = {}
        self.start = None
        self.end = None
        self._start_is_end = False

    def add_node(self, node_id: int):
        self._graph[node_id] = {}
        return node_id

    def add_edge(self, from_node_id: int, to_node_id: int, edge_value):
        if not edge_value in self._graph[from_node_id].keys():
            self._graph[from_node_id][edge_value] = set()
        self._graph[from_node_id][edge_value].add(to_node_id)

    def add_automat(self, other):
        assert set(self._graph.keys()).intersection(set(other._graph.keys())) == set()
        for node_id, node in other._graph.items():
            self._graph[node_id] = node

    def _connected_nodes(self, node_id, edge=-1):
        result = set()
        node = self._graph[node_id]

        result = result.union(node.get(edge, {}))
        result = result.union(node.get(-1, {}))


        for out_id in list(node.get(edge, {})):
            result = result.union(self._connected_nodes(out_id, -1))
        for out_id in list(node.get(-1, {})):
            result = result.union(self._connected_nodes(out_id, edge))

        return result

    def alphabet(self):
        alphabet = set()
        for node in self._graph.values():
            alphabet = alphabet.union(set(node.keys()))
        alphabet.remove(-1)
        return tuple(alphabet)

    def remove_epsilon_edges(self):
        if self.end in self._connected_nodes(self.start, -1):
            self._start_is_end = True
        alphabet = self.alphabet()
        for node_id, node in self._graph.items():
            for c in alphabet:
                for out_node in list(node.get(c, {})):
                    outs = self._connected_nodes(out_node, -1)

                    if not node.get(c, {}):
                        self._graph[node_id][c] = set()
                    self._graph[node_id][c] = node[c].union(outs)

            for epsilon_ounts in list(node.get(-1, {})):
                for c in alphabet:
                    outs = self._connected_nodes(epsilon_ounts, c)
                    if not outs:
                        continue

                    if not node.get(c, {}):
                        self._graph[node_id][c] = set()
                    self._graph[node_id][c] = node[c].union(outs)
            if -1 in node.keys():
                self._graph[node_id].pop(-1)
        print("without epsi", self._graph)

    def dka(self):
        alphabet = self.alphabet()
        self.remove_epsilon_edges()

        table = {frozenset({self.start}): dict()}
        for letter in alphabet:
            table[frozenset({self.start})][letter] = set()
        added = True

        while added:
            added = False
            for states, states_outs in dict(table).items():
                for letter in alphabet:
                    for node_id in list(states):
                        table[states][letter] = table[states][letter].union(self._connected_nodes(node_id, letter))
                    new_state = frozenset(table[states][letter])
                    if not new_state in table.keys() and table[states][letter]:
                        table[new_state] = dict()
                        for c in alphabet:
                            table[new_state][c] = set()
                        added = True

        new_fa = FiniteAutomat()
        new_fa._start_is_end = self._start_is_end
        new_fa.start = self.start
        new_fa.end = self.end
        new_fa._graph = {}
        for state, outs in table.items():
            new_fa._graph[state] = outs
        return new_fa

    def eval(self, input_it: str, mode=MatchMode.MATCH_WHOLE):
        current_node_id = {self.start}

        if mode == FiniteAutomat.MatchMode.MATCH_WHOLE:
            for c in input_it:
                if c.isdigit():
                    next_node_id = self._graph[frozenset(current_node_id)].get("\\d", None)
                else:
                    next_node_id = self._graph[frozenset(current_node_id)].get(c, None)
                if not next_node_id:
                    next_node_id = self._graph[frozenset(current_node_id)].get(c, None)
                print(next_node_id)
                if not next_node_id:
                    print("No match")
                    return False
                current_node_id = next_node_id

            if self.end in current_node_id or (self._start_is_end and self.start in current_node_id):
                print("Match")
                return True
            else:
                print("No match")
                return False

        elif mode == FiniteAutomat.MatchMode.MATCH_SUB:
            for i in range(0, len(input_it)):
                for c in input_it[i::]:
                    next_node_id = self._graph[frozenset(current_node_id)].get(c, None)
                    if not next_node_id:
                        break
                    current_node_id = next_node_id
                    if self.end in current_node_id  or (self._start_is_end and self.start in current_node_id):
                        print("Match", i)
                        return i


            print("No match")
            return False

class FAGenerator:
    _counter = 0

    @staticmethod
    def uid() -> int:
        FAGenerator._counter += 1
        return FAGenerator._counter - 1

    @staticmethod
    def load_c(c: str):
        fa = FiniteAutomat()
        id_1 = fa.add_node(FAGenerator.uid())
        id_2 = fa.add_node(FAGenerator.uid())
        fa.add_edge(id_1, id_2, c)
        fa.start = id_1
        fa.end = id_2

        return fa

    @staticmethod
    def concanate(fa_1: FiniteAutomat, fa_2: FiniteAutomat):
        fa_1.add_automat(fa_2)
        fa_1.add_edge(fa_1.end, fa_2.start, -1)
        fa_1.end = fa_2.end

        return fa_1

    @staticmethod
    def union(fa_1: FiniteAutomat, fa_2: FiniteAutomat):
        fa_1.add_automat(fa_2)
        id_start = fa_1.add_node(FAGenerator.uid())
        id_end = fa_1.add_node(FAGenerator.uid())

        fa_1.add_edge(id_start, fa_1.start, -1)
        fa_1.add_edge(id_start, fa_2.start, -1)

        fa_1.add_edge(fa_1.end, id_end, -1)
        fa_1.add_edge(fa_2.end, id_end, -1)

        fa_1.start = id_start
        fa_1.end = id_end

        return fa_1

    @staticmethod
    def iterate(fa: FiniteAutomat):
        id_start = fa.add_node(FAGenerator.uid())
        id_end = fa.add_node(FAGenerator.uid())

        fa.add_edge(id_start, fa.start, -1)
        fa.add_edge(fa.end, id_end, -1)
        fa.add_edge(fa.end, fa.start, -1)
        fa.add_edge(id_start, id_end, -1)

        fa.start = id_start
        fa.end = id_end

        return fa
