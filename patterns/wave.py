# wave
# Copyright (C) Paul Brook <paul@nowt.org>
# Released under the terms of the GNU General Public License version 3

import random
import cubehelper
import math

speed = 2.0
DT = 1.0/50

class Pattern(object):
    def init(self):
        self.offset = 0.0
        self.double_buffer = True
        self.n = random.choice([1, 2])
        self.color = [cubehelper.random_color() for i in range(0, self.n)]
        return DT

    def plot(self, x, y, z, color):
        l = self.cube.size - 1
        self.cube.set_pixel((x, y, z), color)
        self.cube.set_pixel((l-x, y, z), color)
        self.cube.set_pixel((x, l-y, z), color)
        self.cube.set_pixel((l-x, l-y, z), color)
        self.cube.set_pixel((x, y, z), color)

    def tick(self):
        self.cube.clear()
        self.offset += DT * math.pi * speed
        if self.offset > math.pi * 2.0:
            self.offset -= math.pi * 2.0
        sz = self.cube.size // 2
        scale = math.pi * 2.0 * 0.4 / float(sz)
        for y in range(0, sz):
            for x in range(0, sz):
                if x > y:
                    d = x + y / 2.0
                else:
                    d = y + x / 2.0
                d + 0.5
                dz = math.cos(self.offset + d * scale)
                z = int((dz + 1.0) * (self.cube.size - 1)/ 2.0 + 0.5)
                if z == 8:
                    z = 7
                self.plot(x, y, z, self.color[0])
                if self.n > 1:
                    self.plot(x, y, (self.cube.size - 1) - z, self.color[1])
        raise StopIteration
