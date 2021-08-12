from __future__ import annotations

from .node import Node
import langg.proto.ttop_pb2 as ttop_pb2

import os
import string
import argparse

CONSIDERED_CHARS = list(string.ascii_lowercase) + \
    list(string.whitespace) + ['\'']


class Tree:

    def __init__(self):
        self.name: str = ''
        self.considered_chars: [str] = []
        self.root_chars: [str] = []
        self.root = None

    @classmethod
    def from_cli(cls, infiles: [str], args: argparse.Namespace) -> Tree:
        _self: Tree = Tree()
        _self.name: str = '_'.join(
            [os.path.splitext(os.path.basename(fn))[0] for fn in infiles])
        _self.data: dict[str, [str]] = {fn: [] for fn in infiles}

        _self.root: Node = Node()

        chars_list: [str] = list(args.chars or '')
        _self.considered_chars: [str] = chars_list or CONSIDERED_CHARS

        roots_list: [str] = list(args.root_chars or '')
        _self.root_chars: [str] = roots_list or CONSIDERED_CHARS
        return _self

    @classmethod
    def from_protobuf(cls, tree: ttop_pb2.TreeTop.Tree) -> Tree:
        _self: Tree = Tree()
        _self.name = tree.name
        _self.considered_chars = tree.considered_chars
        _self.root_chars = tree.root_chars
        _self.root = Node.from_protobuf(tree.root)
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

    def _read_words(self, infile) -> [str]:
        with open(infile, 'r') as f:
            contents = f.read()
        warr: [str] = []
        for idx, char in enumerate(contents.lower()):
            if char not in self.considered_chars:
                # Replace non-considered char with spaces, ignoring them will
                #  cause quoted words to join
                char = ' '
            elif char == '\'':
                # Want to keep if an apostrophe, but not if a quote
                if idx > 0 and contents[idx - 1] == ' ':
                    continue
                if idx < len(contents) and contents[idx + 1] == ' ':
                    continue
            warr.append(char)
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
            'infiles': list(self.data.keys()),
            **self.root.to_dict(),
        }
