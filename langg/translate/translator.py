from ..lib.tree import Tree
from ..lib.ttop import TreeTop
from ..util import consts
from .router_vals import (RouterValuesGenerator, RouterValues)

import sys
import argparse
import logging as log


class LineSeparationVals:

    '''Input line-split values

    A custom line separation function was required to account for considered
    chars and keep track of uppercase characters

    Attributes:

        separators: Contiguous non-considered chars

        words: Contiguous considered chars

        upper_idx_pos: Indices of upper case characters per word
            Note: `[-1]` is used to signify that all chars are uppercase

        separate_first: Whether to insert a separator before a word
    '''

    def __init__(self):
        self.separators: [str] = []
        self.words: [str] = []
        self.upper_idx_pos: [[float]] = []
        self.separate_first: bool

    def __str__(self):
        return '{' + \
            f'separators: {self.separators}, ' + \
            f'words: {self.words}, ' + \
            f'upper_idx_pos: {self.upper_idx_pos}, ' + \
            f'separate_first: {self.separate_first}, ' + \
            '}'


class Translator:

    '''Translates the given text with the given tree

    Attributes:

        args: CLI or dictionary args, see :mod:`langg.util.argp`

        op_data: Operation data from the args provided

        tree: The first tree found in the :class:`langg.lib.ttop.TreeTop`

        rvg: Generator of values for routing through the tree, see
            :class:`langg.translate.router_vals.RouterValuesGenerator`

    '''

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

        seed = self.op_data.seed or consts.DEFAULT_SEED
        log.info(f'Running translator with initial seed: {seed}')

        self.rvg = RouterValuesGenerator(seed)

    @classmethod
    def to_text(cls, lines: [[str]]):
        '''Transforms the list of lists of strings to a string'''

        return '\n'.join(
            [''.join([word for line in lines for word in line])])

    def translate_stdin(self) -> None:
        '''Translates text from stdin'''

        for line in sys.stdin:
            lines: [[str]] = self._translate([line])
            print(Translator.to_text(lines))

    def translate_text(self) -> str:
        '''Translates text from the source specified in `op_data`'''

        lines: [[str]] = self._translate(self._read_input().split('\n'))
        return Translator.to_text(lines)

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

    def _split_non_considered_chars(self, _line: str) -> LineSeparationVals:
        '''Splits lines in the input and records separation data'''

        considered: [str] = self.tree.considered_chars
        _line = _line.rstrip()
        line = _line.lower()
        lsv = LineSeparationVals()
        lsv.separate_first = line[0] not in considered

        def _get_while(i: int, bl: bool):
            s: str = ''
            while i < len(line) and (line[i] in considered) is bl:
                s += line[i]
                i += 1
            return s, i

        i: int = 0
        while i < len(line):
            if line[i] in considered:
                start_i: int = i
                s, i = _get_while(i, True)
                lsv.words += [s]
                orig_word: str = _line[start_i:i]
                if orig_word.isupper():
                    lsv.upper_idx_pos.append([-1])
                else:
                    lsv.upper_idx_pos.append(
                        [i / len(orig_word) for i in range(len(orig_word))
                            if orig_word[i].isupper()])
            else:
                s, i = _get_while(i, False)
                lsv.separators += [s]

        log.debug(f'LineSeparationVals: {lsv}')

        return lsv

    def _translate(self, lines: [str]) -> str:
        '''Generates a seed per phrase and traverses the tree to form words'''

        output: [str] = []
        for line in lines:
            line_output: [str] = []

            # There will always be one less separator than there are words
            lsv: LineSeparationVals = self._split_non_considered_chars(line)

            i: int = 0
            while i < len(lsv.words):
                phrase: [str] = lsv.words[i:i+2]
                rv: RouterValues = self.rvg.router_vals(phrase)
                word: str = self.tree.build_word(self.rvg, rv)

                # Captial letters
                upper_idx_pos: [float] = lsv.upper_idx_pos[i]

                # Special case for all caps word
                if len(upper_idx_pos) == 1 and upper_idx_pos[0] == -1:
                    word = word.upper()
                else:
                    if rv.merge_words and i + 1 < len(lsv.words):
                        upper_idx_pos += lsv.upper_idx_pos[i + 1]

                    for pos in upper_idx_pos:
                        new_pos: int = int(pos * len(word))
                        word = word[:new_pos] + \
                            word[new_pos].upper() + word[new_pos + 1:]

                # Merge words
                if rv.merge_words:
                    i += 1
                    idx: int = self.rvg.contract_at(word)
                    word = word[:idx] + '\'' + word[idx:]
                if lsv.separate_first:
                    if i < len(lsv.separators) and not rv.merge_words:
                        line_output.append(lsv.separators[i])
                    line_output.append(word)
                else:
                    line_output.append(word)
                    if i < len(lsv.separators) and not rv.merge_words:
                        line_output.append(lsv.separators[i])
                i += 1
            output.append(line_output)
        return output
