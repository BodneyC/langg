from __future__ import annotations

from .tree import Tree
from ..util.namespace import Namespace
import langg.proto.ttop_pb2 as ttop_pb2

import os
import json
import logging
from typing import Optional

LOG: logging.Logger = logging.getLogger('TreeTop')


class TreeTop:
    '''Container class for :class:`langg.lib.tree.Tree`s'''

    def __init__(self):
        self.trees: [Tree] = []

    # Construction methods

    @classmethod
    def for_bot(cls, fn: str) -> TreeTop:
        '''Construct a TreeTop for the discord bot'''

        _self: TreeTop = TreeTop()
        _self.trees = [Tree.for_bot(fn)]
        _self.op_data = Namespace(full=True)
        return _self

    @classmethod
    def from_cli(cls, args: Namespace) -> TreeTop:
        '''Construct a TreeTop from a dictionary file'''

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
    def from_protobuf(cls, fn: str) -> Optional[TreeTop]:
        '''Construct a TreeTop from a protobuf output from langg'''

        if not os.path.isfile(fn):
            LOG.error(f'No such proto file: {fn}')
            return None

        ttop = ttop_pb2.TreeTop()
        with open(fn, 'rb') as f:
            ttop.ParseFromString(f.read())
        _self: TreeTop = TreeTop()
        for tree in ttop.tree:
            _self.trees.append(Tree.from_protobuf(tree))
        return _self

    @classmethod
    def from_json(cls, fn: str) -> TreeTop:
        '''Construct a TreeTop by deserialising a JSON file'''

        if not os.path.isfile(fn):
            LOG.error(f'No such JSON file: {fn}')
            return None

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
        '''Serialise to a protobuf object'''

        ttop_proto = ttop_pb2.TreeTop()
        for tree in self.trees:
            tree.to_protobuf(ttop_proto.tree.add())
        return ttop_proto

    # IO methods

    def write_dot(self, fn: str):
        with open(fn, 'w') as f:
            f.write(self.to_dot())

    def to_dot(self) -> str:
        '''Create a dotviz graph file'''

        return '\n'.join([tree.to_dot() for tree in self.trees])

    def write_json(self, fn: str):
        with open(fn, 'w') as f:
            f.write(json.dumps(self.to_dict()))

    def to_json(self):
        '''Serialise to JSON'''

        return json.dumps(self.to_dict(), indent=2)

    def to_dict(self) -> dict:
        return [tree.to_dict() for tree in self.trees]
