# Walk over sides of a cube
# Copyright (C) Paul Brook <paul@nowt.org>
# Released under the terms of the GNU General Public License version 3

import cubehelper
import random

class Pattern(object):
    def init(self):
        self.axes = (0, 2, 1)
        self.mirror = [True, False, False]
        self.offset = 0.0
        self.delta = 0.1 * self.cube.size
        self.color = cubehelper.random_color()
        self.double_buffer = True
        return 0.1
    def plot(self, x):
        cubepos = [0]*3
        lim = self.cube.size - 1
        for n in range(0, 3):
            val = x[n]
            if self.mirror[n]:
                val = lim - val
            cubepos[self.axes[n]] = val
        self.cube.set_pixel(cubepos, self.color)
    def permute_axes(self, order):
        self.axes = tuple([self.axes[n] for n in order])
        self.mirror = [self.mirror[n] for n in order]
    def tick(self):
        self.cube.clear()
        sz = self.cube.size
        y = 0.5
        step = self.offset / (sz - 1)
        for x in range(0, sz):
            for z in range(0, sz):
                self.plot((x, int(y), z))
            y += step
        self.offset += self.delta
        if self.offset >= sz - 1:
            self.offset = 2 * (sz - 1) - self.offset
            self.delta = -self.delta
            self.permute_axes((1, 0, 2))
        if self.offset < 0.0:
            self.offset = -self.offset
            self.delta = -self.delta
            n = random.randrange(3)
            if n > 0:
                self.permute_axes((2, 1, 0))
            if n < 2:
                self.mirror[0] = not self.mirror[0]
