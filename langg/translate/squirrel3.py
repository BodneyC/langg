class Squirrel3:
    BIT_NOISE_1: int = 0xB5297A4D
    BIT_NOISE_2: int = 0x68E31DA4
    BIT_NOISE_3: int = 0x1B56C4E9

    position: int = -1

    def rand(self, position: int, seed: int = 0):
        position *= Squirrel3.BIT_NOISE_1
        position += seed
        position ^= (position >> 8)
        position += Squirrel3.BIT_NOISE_2
        position ^= (position << 8)
        position *= Squirrel3.BIT_NOISE_3
        position ^= (position >> 8)
        return position

    def i32(self, seed: int):
        self.position += 1
        return self.rand(self.position, seed)

    def i32range(self, seed: int, max: int, min: int = 0) -> int:
        return (self.i32(seed) & (max - min)) + min

    def f53(self, seed: int):
        return self.i32(seed) / 0xFFFFFFFF
