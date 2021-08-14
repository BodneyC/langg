from __future__ import annotations

from .tree import Tree
import langg.proto.ttop_pb2 as ttop_pb2

import json
import argparse


class TreeTop:

    def __init__(self):
        self.trees: [Tree] = []

    # Construction methods

    @classmethod
    def from_cli(cls, args: argparse.Namespace) -> TreeTop:
        _self: TreeTop = TreeTop()
        _self.args = args
        _self.op_data = args.op_data
        if _self.op_data.separate_trees:
            _self.trees = [Tree.from_cli(infile, args)
                           for infile in args.infiles]
        else:
            _self.trees = [Tree.from_cli(args.infiles, args)]
        return _self

    def parse_infiles(self):
        for tree in self.trees:
            tree.parse_infiles(self.op_data.full)

    @classmethod
    def from_protobuf(cls, fn: str) -> TreeTop:
        ttop = ttop_pb2.TreeTop()
        with open(fn, 'rb') as f:
            ttop.ParseFromString(f.read())
        _self: TreeTop = TreeTop()
        for tree in ttop.tree:
            _self.trees.append(Tree.from_protobuf(tree))
        return _self

    @classmethod
    def from_json(cls, fn: str) -> TreeTop:
        with open(fn, 'rb') as f:
            ttop = json.load(f)
        _self: TreeTop = TreeTop()
        for tree in ttop:
            _self.trees.append(Tree.from_json(tree))
        return _self

    # Traversal methods

    def sort_trees(self):
        for tree in self.trees:
            tree.sort_tree()

    def statistics(self) -> dict:
        return {
            tree.name: {
                'node_count': tree.node_count(),
                'longest_branch': tree.longest_branch(),
                'k_length_prefixes': tree.k_length_prefixes(self.args.kmers),
            }
            for tree in self.trees
        }

    # Protobuf methods

    def write_protobuf(self, fn: str):
        with open(fn, 'wb') as f:
            f.write(self.to_protobuf().SerializeToString())

    def to_protobuf(self) -> ttop_pb2.TreeTop:
        ttop_proto = ttop_pb2.TreeTop()
        for tree in self.trees:
            tree.to_protobuf(ttop_proto.tree.add())
        return ttop_proto

    # IO methods

    def write_dot(self, fn: str):
        with open(fn, 'w') as f:
            f.write(self.to_dot())

    def to_dot(self) -> str:
        return '\n'.join([tree.to_dot() for tree in self.trees])

    def write_json(self, fn: str):
        with open(fn, 'w') as f:
            f.write(json.dumps(self.to_dict()))

    def to_json(self):
        return json.dumps(self.to_dict(), indent=2)

    def to_dict(self) -> dict:
        return [tree.to_dict() for tree in self.trees]
