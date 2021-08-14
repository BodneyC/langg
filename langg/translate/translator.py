from ..lib.tree import Tree
from ..lib.ttop import TreeTop
from ..util import consts
from ..util.mt19937_64 import MT19937_64

import sys
import argparse
import logging as log


class Translator:
    def __init__(self, ttop: TreeTop, args: argparse.Namespace):
        self.args = args
        self.op_data = args.op_data

        if not ttop.trees:
            raise Exception('TreeTop provided contains no trees')

        tree_n: int = self.op_data.tree
        if tree_n < 0 or tree_n >= len(ttop.trees):
            raise Exception(
                f'Tree index {str(tree_n)} specified not in TreeTop')

        self.tree: Tree = ttop.trees[tree_n]

        self.seed = args.seed or consts.DEFAULT_SEED
        log.info(f'Running translator with seed: {self.seed}')

        self.mt = MT19937_64()

    def translate(self):
        if self.op_data.stdin:
            for line in sys.stdin:
                self._translate([line])
        else:
            self._translate(self._read_input().split('\n'))

    def _read_input(self) -> str:
        if self.op_data.txt:
            return self.op_data.txt
        if self.op_data.txt_in:
            data = []
            for fn in self.op_data.txt_in:
                with open(fn, 'r') as f:
                    data += f.read().split()
            return '\n'.join(data)
        raise Exception('Unknown input type')

    def _translate(self, lines: [str]) -> str:
        pass  # Todo
