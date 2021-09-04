from .squirrel3 import Squirrel3

from typing import Optional


class Squirrel3RNG:
    '''Squirrel3 class wrapper

    As noise functions inherently have no sense of state where RNG's tend to
     this class is to wrap :class:`langg.translate.squirrel3.Squirrel3` and
     make it act as an RNG

    Attributes:

        rng: Instance of :class:`langg.translate.squirrel3.Squirrel3`

        seed: Nullable seed, should fail if null
    '''

    def __init__(self):
        self.rng = Squirrel3()
        self._seed: Optional[int] = None

    def seed(self, seed: int):
        '''Set the seed and reset the `y` coord'''
        self._seed = seed
        self.rng.position = -1

    def i32(self):
        '''Get a 32-bit integer'''
        return self.rng.i32(self._seed)

    def i32range(self, max: int, min: int = 0) -> int:
        '''Get a 32-bit integer within a certain range'''
        return self.rng.i32range(self._seed, max, min)

    def f53(self):
        '''Get a floating point number (53-bit as is Python's standard)'''
        return self.rng.f53(self._seed)

    def f53_inclusive(self) -> float:
        '''Real number in [0, 1]'''
        return self.rng.f53_inclusive(self._seed)

    def f53_exclusive(self) -> float:
        '''Real number in [0, 1)'''
        return self.rng.f53_exclusive(self._seed)
