from .squirrel3 import Squirrel3

import logging as log

I32_BYTE_WIDTH: int = 4
MERGE_WORDS_OFFSET: float = 0.92
WORD_VARIATION_MAX: int = 6


class RouterValues:
    merge_words: bool
    max_depth: int
    word_length: int


class RouterValuesGenerator:

    def __init__(self, seed: int):
        self.seed = seed
        self.rng = Squirrel3()
        # +[0, 5]%
        self.merge_words_prob: float = MERGE_WORDS_OFFSET + \
            (self.rng.f53(seed=self.seed) / 20)

    def rng_reset(self):
        self.rng.position = -1

    def gen_seed(self, words: [str]):
        seed: int = self.seed
        word_str: str = ' '.join(words)
        mod32: int = len(word_str) % I32_BYTE_WIDTH
        word_str = word_str + word_str[-mod32:] * (I32_BYTE_WIDTH * mod32)
        arr: [int] = [ord(s) for s in word_str]

        for i in range(0, len(arr), I32_BYTE_WIDTH):
            seed ^= int.from_bytes(bytearray(arr[i:i+I32_BYTE_WIDTH]), 'big')
        return seed

    def word_length(self, seed: int, words: [str]) -> int:
        base_len: int
        if len(words) == 1:
            base_len = len(words[0])
        else:
            base_len = sum(len(w) for w in words) / len(words)

        word_variation: int = min(base_len, WORD_VARIATION_MAX)

        word_variation = self.rng.i32range(
            seed=seed,
            max=word_variation * 2) - word_variation

        log.debug(f'Word variation: {word_variation}')

        if base_len + word_variation < 1:
            word_variation = abs(word_variation)

        return base_len + word_variation

    def router_vals(self, seed: int, words: [str]) -> RouterValues:
        rv = RouterValues()

        rv.merge_words = False
        if len(words) > 1:
            rv.merge_words = self.rng.f53(seed=seed) > self.merge_words_prob

        rv.max_depth: int = self.rng.i32range(seed=seed, max=6, min=2)

        rv.word_length = self.word_length(seed, words)

        return rv

    def child_idx(self, seed: int, visits: [int]) -> int:
        if len(visits) == 0:
            return -1
        expanded = []
        for i, visit in enumerate(visits):
            expanded += [i] * visit
        idx: int = self.rng.i32range(seed=seed, max=len(expanded) - 1)
        return expanded[idx]
