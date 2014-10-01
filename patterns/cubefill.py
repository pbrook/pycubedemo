# Fill the cube with a solid colour, starting from random corners
# Copyright (C) Alex Silcock <alex@alexsilcock.net>
# Released under the terms of the GNU General Public License version 3

import cubehelper
import math
import random

# range is inclusive
def in_range(x, a, b):
    return (x >= a) and (x <= b)

class Pattern(object):
    def init(self):
        self.double_buffer = True
        # Vertices:
        # bottom layer
        # 2--6
        # |  |
        # 0--4
        #
        # top layer
        # 3--7
        # |  |
        # 1--5

        cs = self.cube.size-1

        self.corners = [
            [(0, 0, 0), (1, 1, 1)],       # 0
            [(0, 0, cs), (1, 1, -1)],     # 1
            [(0, cs, 0), (1, -1, 1)],     # 2
            [(0, cs, cs), (1, -1, -1)],   # 3
            [(cs, 0, 0), (-1, 1, 1)],     # 4
            [(cs, 0, cs), (-1, 1, -1)],   # 5
            [(cs, cs, 0), (-1, -1, 1)],   # 6
            [(cs, cs, cs), (-1, -1, -1)], # 7
        ]

        self.filling_color = 0
        self.restart()
        return 0.6 / self.cube.size

    def restart(self):
        self.offset = 0
        self.corner = self.corners[random.randrange(0, 8)]
        self.filling_color = cubehelper.random_color(self.filling_color)

    def tick(self):
        pos = self.corner[0]
        outer = self.offset
        inner = self.offset - 4

        for y in range(self.cube.size):
            dy = abs(y - pos[1])
            for x in range(self.cube.size):
                dx = abs(x - pos[0])
                for z in range(self.cube.size):
                    dz = abs(z - pos[0])
                    if max(dx, dy, dz) >= inner and max(dx, dy, dz) <= outer:
                        color = self.filling_color
                    else:
                        color = 0
                    self.cube.set_pixel((x, y, z), color)

        if inner == self.cube.size:
            self.restart()
            raise StopIteration
        else:
            self.offset += 1
