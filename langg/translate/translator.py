from ..lib.tree import Tree
from ..lib.ttop import TreeTop
from ..util import consts
from .router_vals import (RouterValuesGenerator, RouterValues)

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

        self.seed = self.op_data.seed or consts.DEFAULT_SEED
        log.info(f'Running translator with seed: {self.seed}')

        self.rvg = RouterValuesGenerator(self.seed)

    def translate_stdin(self) -> None:
        for line in sys.stdin:
            print(self._translate([line]))

    def translate_text(self) -> str:
        lines: [[str]] = self._translate(self._read_input().split('\n'))
        return '\n'.join([' '.join([word for line in lines for word in line])])

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
        # Todo:
        #  - Handle considered_chars
        #  - Handle cases
        output: [str] = []
        for line in lines:
            line_output: [str] = []
            words: [str] = line.split()
            for i in range(len(words)):
                self.rvg.rng_reset()
                phrase: [str] = words[i:i+1]
                seed: int = self.rvg.gen_seed(phrase)
                rv: RouterValues = self.rvg.router_vals(seed, phrase)
                word: str = self.tree.build_word(self.rvg, rv, seed)
                if rv.merge_words:
                    i += 1
                line_output.append(word)
            output.append(line_output)
        return output
