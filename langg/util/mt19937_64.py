#!/usr/bin/env python3

# Mostly stolen from:
#
#  https://github.com/alexforencich/verilog-mersenne/blob/master/tb/mt19937_64.py
#
# but with a few "readability" changes (mostly the reduction of magic
#  numbers...)
#
# I should say that this file only exists because I didn't know if this would
#  end up in Python and wanted to be able to generate the same numbers from the
#  same seeds in other languages

DEF_SEED = 5489
ARR_SEED = 19650218
STATE_SZ = 312
STATE_M1 = STATE_SZ - 1
STATE_P1 = STATE_SZ + 1
STATE_2X = 624
SHIFT_SZ = 156
INIT_MUL = 6364136223846793005
TEMPER_B = 0x71D67FFFEDA60000
TEMPER_C = 0xFFF7EEE000000000
TEMPER_D = 0x5555555555555555
XOR_MASK = 0xB5026F5AA96619E9
C_1 = 3935559000370003845
C_3 = 2862933555777941757


class MT19937_64:
    mt: [int] = [0] * STATE_SZ
    mti: int = STATE_P1

    # ------------------------------------------------------------------------
    # Internal methods
    # ------------------------------------------------------------------------

    def _int64(self, n: int) -> int:
        return n & 0xFFFFFFFFFFFFFFFF

    def _lmask(self, n: int) -> int:
        return n & 0xFFFFFFFF80000000

    def _rmask(self, n: int) -> int:
        return n & 0x000000007fffffff

    def _bit_manip(self) -> int:
        y = self.mt[self.mti]
        self.mti += 1

        y ^= (y >> 29) & TEMPER_D
        y ^= (y << 17) & TEMPER_B
        y ^= (y << 37) & TEMPER_C
        y ^= (y >> 43)

        return y

    # ------------------------------------------------------------------------
    # Seeding
    # ------------------------------------------------------------------------

    def seed(self, seed: int) -> None:
        self.mt[0] = self._int64(seed)
        for i in range(1, STATE_SZ):
            self.mt[i] = self._int64(INIT_MUL * (
                self.mt[i - 1] ^ (self.mt[i - 1] >> 62)
            ) + i)
        self.mti = STATE_SZ

    def composite_seed(self, key: [int]) -> None:
        self.seed(ARR_SEED)
        i, j = 1, 0
        k = max(STATE_SZ, len(key))
        for ki in range(k):
            self.mt[i] = self._int64((self.mt[i] ^ ((
                self.mt[i - 1] ^ (self.mt[i - 1] >> 62)
            ) * C_1)) + key[j] + j)
            i += 1
            j += 1
            if i >= STATE_SZ:
                self.mt[0] = self.mt[STATE_M1]
                i = 1
            if j >= len(key):
                j = 0
        for ki in range(STATE_SZ):
            self.mt[i] = self._int64((self.mt[i] ^ ((
                self.mt[i - 1] ^ (self.mt[i - 1] >> 62)
            ) * C_3)) - i)
            i += 1
            if i >= STATE_SZ:
                self.mt[0] = self.mt[STATE_M1]
                i = 1
        self.mt[0] = 1 << 63

    # ------------------------------------------------------------------------
    # Random 64-bit number generation
    # ------------------------------------------------------------------------

    def int64(self) -> int:
        if self.mti < STATE_SZ:
            return self._bit_manip()

        if self.mti == STATE_P1:
            self.seed(DEF_SEED)

        for k in range(STATE_M1):
            y: int = self._lmask(self.mt[k]) | self._rmask(self.mt[k + 1])
            mask: int = XOR_MASK if y & 1 else 0
            if k < STATE_SZ - SHIFT_SZ:
                self.mt[k] = self.mt[k + SHIFT_SZ] ^ (y >> 1) ^ mask
            else:
                self.mt[k] = self.mt[k + SHIFT_SZ - STATE_2X] ^ (y >> 1) ^ mask

        y = self._lmask(self.mt[STATE_M1]) | self._rmask(self.mt[0])
        self.mt[STATE_M1] = self.mt[155] ^\
            (y >> 1) ^ (XOR_MASK if y & 1 else 0)
        self.mti = 0

        return self._bit_manip()

    # Note: I, straight up, have no idea of the purpose of this method... i.e.
    #       how it differs from `self.int64()` - I can see the different lines
    #       but I don't know the functional difference(s)
    def int64b(self) -> int:
        if self.mti == STATE_P1:
            self.seed(DEF_SEED)

        k: int = self.mti

        if k == STATE_SZ:
            k = self.mti = 0

        if k == STATE_M1:
            y: int = self._lmask(self.mt[STATE_M1]) | self._rmask(self.mt[0])
            mask: int = XOR_MASK if y & 1 else 0
            self.mt[STATE_M1] = self.mt[155] ^ (y >> 1) ^ mask

        else:
            y: int = self.lmask(self.mt[k]) | self._rmask(self.mt[k+1])
            mask: int = XOR_MASK if y & 1 else 0
            if k < STATE_SZ - SHIFT_SZ:
                self.mt[k] = self.mt[k + SHIFT_SZ] ^ (y >> 1) ^ mask
            else:
                self.mt[k] = self.mt[k + SHIFT_SZ - STATE_2X] ^ (y >> 1) ^ mask

        return self._bit_manip()


if __name__ == '__main__':
    mt = MT19937_64()
    mt.composite_seed([0x12345, 0x56789])
    n: int = 10
    for i in range(n):
        print(mt.int64())
