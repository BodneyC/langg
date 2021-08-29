I32_FULL: int = 0xFFFFFFFF

BIT_NOISE_1: int = 0xB5297A4D
BIT_NOISE_2: int = 0x68E31DA4
BIT_NOISE_3: int = 0x1B56C4E9


class Squirrel3:
    '''Squirrel3 noise function wrapper

    I saw this in a GDC talk but I can't find this to credit the chap. For my
     purposes it is essentially a lightweight alternative to the tradition
     RNGs

    I also didn't know what language this program would end up in so having
     something simple I can manually transpile was useful

    Attributes:

        position: If the seed is our x coordinate, the position is our y
            Useful if you want a `next` function of sorts
    '''

    position: int = -1

    def reset(self):
        self.position = -1

    def rand(self, position: int, seed: int = 0):
        position *= BIT_NOISE_1
        position += seed
        position ^= (position >> 8)
        position += BIT_NOISE_2
        position ^= (position << 8)
        position *= BIT_NOISE_3
        position ^= (position >> 8)
        return position & I32_FULL

    def i32(self, seed: int):
        '''Get a 32-bit integer'''

        self.position += 1
        return self.rand(self.position, seed)

    def i32range(self, seed: int, max: int, min: int = 0) -> int:
        '''Get a 32-bit integer within a certain range'''

        return (self.i32(seed) & (max - min)) + min

    def f53(self, seed: int):
        '''Get a floating point number (53-bit as is Python's standard)'''

        return self.i32(seed) / I32_FULL
