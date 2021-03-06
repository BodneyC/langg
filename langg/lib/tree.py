from __future__ import annotations

from .node import Node
from ..util import consts
import langg.proto.ttop_pb2 as ttop_pb2
from ..translate.router_vals import (RouterValuesGenerator, RouterValues)


import os
from types import SimpleNamespace


class Tree:
    '''Contains and manages the root node our our langg tree

    Attributes:

        name: Usually the dictionary filename which created this tree

        considered_chars: Chars to consider while constructing trees

        root_chars: Similar to `considered_chars` but only affecting the
            root node

        root: Root node (see :class:`langg.lib.node.Node`) of the tree
    '''

    def __init__(self):
        self.name: str = ''
        self.considered_chars: [str] = []
        self.root_chars: [str] = []
        self.root = None

    @classmethod
    def for_bot(cls, fn: str) -> Tree:
        _self: Tree = Tree()
        _self.name: str = fn
        _self.data: dict[str, [str]] = {fn: []}

        _self.root: Node = Node()

        _self.considered_chars: [str] = consts.CONSIDERED_CHARS

        _self.root_chars: [str] = consts.CONSIDERED_CHARS
        return _self

    @classmethod
    def from_cli(cls, infiles: [str], args: SimpleNamespace) -> Tree:
        _self: Tree = Tree()
        _self.name: str = '_'.join(
            [os.path.splitext(os.path.basename(fn))[0] for fn in infiles])
        _self.data: dict[str, [str]] = {fn: [] for fn in infiles}

        _self.root: Node = Node()

        chars_list: [str] = list(args.op_data.root_chars or '')
        _self.considered_chars: [str] = chars_list or consts.CONSIDERED_CHARS

        roots_list: [str] = list(args.op_data.root_chars or '')
        _self.root_chars: [str] = roots_list or consts.CONSIDERED_CHARS
        return _self

    @classmethod
    def from_protobuf(cls, tree: ttop_pb2.TreeTop.Tree) -> Tree:
        _self: Tree = Tree()
        _self.name = tree.name
        _self.considered_chars = list(tree.considered_chars)
        _self.root_chars = list(tree.root_chars)
        _self.root = Node.from_protobuf(tree.root)
        return _self

    @classmethod
    def from_json(cls, tree: dict) -> Tree:
        _self: Tree = Tree()
        _self.name = tree['name']
        _self.considered_chars = tree['considered_chars']
        _self.root_chars = tree['root_chars']
        _self.root = Node.from_json(tree['root'])
        return _self

    def to_protobuf(self, tree: ttop_pb2.TreeTop.Tree) -> None:
        tree.name = self.name
        tree.considered_chars.extend(self.considered_chars)
        tree.root_chars.extend(self.root_chars)
        self.root.to_protobuf(tree.root)

    def parse_infiles(self, full_words: bool = False) -> None:
        for infile in self.data:
            self.data[infile] = self._read_words(infile)
            for word in self.data[infile]:
                if word[0] not in self.root_chars:
                    continue
                if full_words:
                    self.root.parse_word(word)
                else:
                    for i in range(len(word)):
                        self.root.parse_word(word[i:])

    def _considered(self, c: str):
        return c in self.considered_chars or c in consts.WHITESPACE_CHARS

    def _read_words(self, infile) -> [str]:
        with open(infile, 'r') as f:
            contents = f.read()
        warr: [str] = []
        for i, c in enumerate(contents.lower()):
            if not self._considered(c):
                # Replace non-considered char with spaces, ignoring them will
                #  cause quoted words to join
                c = ' '
            elif c == '\'':
                # Want to keep if an apostrophe, but not if a quote
                if i > 0 and contents[i - 1] == ' ':
                    continue
                if i < len(contents) and contents[i + 1] == ' ':
                    continue
            warr.append(c)
        return ''.join(warr).split()

    def node_count(self) -> int:
        return self.root.node_count()

    def longest_branch(self) -> dict:
        longest: [(str, int)] = self.root.longest_branch()
        return {
            'string': ''.join(t[0] for t in longest),
            'visits': [{t[0]: t[1]} for t in longest],
            'length': len(longest),
        }

    def k_length_prefixes(self, k: int) -> dict:
        out: [] = []
        self.root.k_length_prefixes(k=k, out=out)
        return {
            'k': k,
            'list': [
                ''.join([tt[0] for tt in t]) for t in out
            ],
            'prefixes': [{
                'string': ''.join([tt[0] for tt in t]),
                'count': [tt[1] for tt in t][-1],
                'visits': [{tt[0]: tt[1]} for tt in t]
            } for t in out]
        }

    def sort_tree(self):
        self.root.sort_tree()

    def to_dot(self) -> str:
        graph_name: str = self.name.replace('.', '_').replace('-', '_')
        return f'strict digraph {graph_name} {{\n{self.root.to_dot()}}}'

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'root_chars': self.root_chars,
            'considered_chars': self.considered_chars,
            'root': self.root.to_dict(),
        }

    def build_word(self, rvg: RouterValuesGenerator,
                   rv: RouterValues) -> str:
        word: str = ''
        depth: int = 0
        node = self.root
        while len(word) < rv.word_length:
            if depth < rv.max_depth:
                if node.char in self.root.children:
                    node = self.root.children[node.char]
                else:
                    node = self.root
            idx: int = rvg.child_idx(
                [v.visits for v in node.children.values()])
            # print(f'N children ({len(node.children)})')
            if idx == -1:
                if node.char in self.root.children:
                    node = self.root.children[node.char]
                else:
                    node = self.root
                continue
            node: Node = node.children[list(node.children.keys())[idx]]
            depth += 1
            word += node.char
        return word
