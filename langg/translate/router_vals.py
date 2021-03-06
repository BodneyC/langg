from .squirrel3_rng import Squirrel3RNG

import logging as log

I32_BYTE_WIDTH: int = 4
MERGE_WORDS_OFFSET: float = 0.92
WORD_VARIATION_MAX: int = 3


class RouterValues:
    '''Values used by the translator via the router

    Many values are needed in parsing a phrase and assessing how the translate
     should act

    Attributes:

        merge_words: Should the translator merge the words of the phrase

        max_depth: Maximum tree traversal depth before selecting a new root

        word_length: Length of the word in question
    '''

    def __init__(self):
        self.merge_words: bool
        self.max_depth: int
        self.word_length: int

    def __str__(self):
        return '{' + \
            f'merge_words: {self.merge_words}, ' + \
            f'max_depth: {self.max_depth}, ' + \
            f'word_length: {self.word_length}, ' + \
            '}'


class RouterValuesGenerator:
    '''Used to populate :class:`langg.translate.router_vals.RouterValues`'''

    def __init__(self, seed: int):
        self.init_seed = seed
        self.rng = Squirrel3RNG()
        self.rng.seed(self.init_seed)
        # +[0, 5]%
        self.merge_words_prob: float = MERGE_WORDS_OFFSET + \
            (self.rng.f53() / 20)

    @classmethod
    def gen_seed(cls, init_seed: int, word: str) -> int:
        seed: int = init_seed
        mod32: int = len(word) % I32_BYTE_WIDTH
        if mod32 != 0:
            mod32i: int = I32_BYTE_WIDTH - mod32
            word = word + (word[:mod32i] * mod32i)[:mod32i]

        arr: [int] = [ord(s) for s in word]

        for i in range(0, len(arr), I32_BYTE_WIDTH):
            seed ^= int.from_bytes(bytearray(arr[i:i+I32_BYTE_WIDTH]), 'big')

        return seed

    def _gen_seed(self, word: str) -> int:
        '''Generate a seed for the RNG based on a given string'''

        return RouterValuesGenerator.gen_seed(self.init_seed, word)

    def _word_len(self, words: [str]) -> int:
        base_len: int
        if len(words) == 1:
            base_len = len(words[0])
        else:
            base_len = int(sum(len(w) for w in words) / len(words))

        variation_max: int = min(base_len, WORD_VARIATION_MAX)

        variation_arr: [int] = []
        for i in range(variation_max):
            variation_arr += [i] * (variation_max - i)

        word_variation: int = variation_arr[
            self.rng.i32range(max=len(variation_arr) - 1)
        ]

        if base_len + word_variation < 1:
            word_variation = abs(word_variation)

        return base_len + word_variation

    def router_vals(self, words: [str]) -> RouterValues:
        rv = RouterValues()

        self.rng.seed(self._gen_seed(''.join(words)))

        rv.merge_words = False
        if len(words) > 1:
            rv.merge_words = self.rng.f53() > self.merge_words_prob

        self.rng.seed(self._gen_seed(words[0]))

        rv.max_depth: int = self.rng.i32range(max=10, min=4)

        rv.word_length = self._word_len(words)

        log.debug(f'Router values: {rv}')

        return rv

    def contract_at(self, word: str):
        return self.rng.i32range(max=len(word) - 1, min=1)

    def child_idx(self, visits: [int]) -> int:
        if len(visits) == 0:
            return -1
        expanded = []
        for i, visit in enumerate(visits):
            expanded += [i] * visit
        idx: int = self.rng.i32range(max=len(expanded) - 1)
        return expanded[idx]
