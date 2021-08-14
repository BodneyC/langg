from __future__ import annotations

import langg.proto.ttop_pb2 as ttop_pb2

import json
from copy import deepcopy


class Node:

    def __init__(self, char=' ', level=0):
        self.char = char
        self.children: dict[str, Node] = {}
        self.visits: int = 0
        self.depth: int = level

    @classmethod
    def from_protobuf(cls, node: ttop_pb2.TreeTop.Tree.Node) -> Node:
        _self: Node = Node()
        _self.char = node.char
        _self.depth = node.depth
        _self.visits = node.visits
        for e in node.children:
            _self.children[e.char] = Node.from_protobuf(e)
        return _self

    @classmethod
    def from_json(cls, node: dict) -> Node:
        _self: Node = Node()
        _self.char = node['char']
        _self.depth = node['depth']
        _self.visits = node['visits']
        if node['children']:
            for k, v in node['children'].items():
                _self.children[k] = Node.from_json(v)
        return _self

    def __str__(self):
        return json.dumps(self.to_dict())

    def _id(self):
        return str(id(self))

    def parse_word(self, word: str) -> None:
        self.visits += 1
        if not len(word):
            return
        char, word = word[0], word[1:]
        if char not in self.children:
            self.children[char] = Node(
                char=char, level=self.depth + 1)
        self.children[char].parse_word(word)

    def sort_tree(self):
        self.children = dict(sorted(self.children.items()))
        for v in self.children.values():
            v.sort_tree()

    def to_protobuf(self, node: ttop_pb2.TreeTop.Tree.Node) -> None:
        node.char = self.char
        node.depth = self.depth
        node.visits = self.visits
        for k, v in self.children.items():
            v.to_protobuf(node.children.add())

    # Should pretty much be the longest word...
    def longest_branch(self, chars: [(str, int)] = []) -> [(str, int)]:
        if (self.char != ' '):
            chars.append((self.char, self.visits))

        if len(self.children) == 0:
            return chars

        branches: [[(str, int)]] = [v.longest_branch(deepcopy(chars))
                                    for v in self.children.values()]

        return max(branches, key=len)

    def node_count(self) -> int:
        return sum([v.node_count() for v in self.children.values()]) + 1

    def k_length_prefixes(
            self, k: int, out: [], chars: [(str, int)] = []
    ) -> [[[(str, int)]]]:

        if (self.char != ' '):
            chars.append((self.char, self.visits))

        if self.depth == k:
            out.append(chars)
            return

        for v in self.children.values():
            v.k_length_prefixes(k, out, deepcopy(chars))

    def k_length_suffixes(self):
        pass

    def to_dot(self):
        indent: str = ' ' * (self.depth + 1)
        id: str = self._id()

        s: str = ''
        s += f'{indent}{id} [label="{self.char} ({self.visits})"]\n'

        for v in self.children.values():
            s += f'{indent}{id} -> {v._id()}\n'

        for v in self.children.values():
            s += v.to_dot()

        return s

    def to_dict(self):
        return {
            **self.__dict__,
            'children': {k: v.to_dict() for k, v in self.children.items()},
        }


if __name__ == '__main__':
    node: Node = Node()
    node.parse_word('hello')
    print(node)
