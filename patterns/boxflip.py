# Walk over sides of a cube
# Copyright (C) Paul Brook <paul@nowt.org>
# Released under the terms of the GNU General Public License version 3

import cubehelper
import random

class Pattern(object):
    def init(self):
        self.axis0 = 0
        self.axis1 = 1
        self.axis2 = 2
        self.mirror0 = False
        self.mirror1 = False
        self.offset = 0.0
        self.delta = 0.1
        self.color = self.pick_color()
        self.next_color = self.pick_color()
        self.double_buffer = True
        return 0.05
    def pick_color(self):
        if self.cube.color:
            return cubehelper.random_color()
        return (1.0, 1.0, 1.0)
    def tick(self):
        self.cube.clear()
        sz = self.cube.size
        y = 0.5
        step = self.offset
        if self.delta > 0:
            cfrac = self.offset
        else:
            cfrac = 2.0 - self.offset
        color = cubehelper.mix_color(self.color, self.next_color, cfrac/2.0)
        cubepos = [0]*3
        for x in range(0, sz):
            if self.mirror0:
                val = (sz - 1) - x
            else:
                val = x
            cubepos[self.axis0] = val
            val = int(y)
            if self.mirror1:
                val = (sz - 1) - val
            cubepos[self.axis1] = val
            for z in range(0, sz):
                cubepos[self.axis2] = z
                self.cube.set_pixel(cubepos, color)
            y += step
        self.offset += self.delta
        if self.offset >= 1.0:
            self.offset = 2.0 - self.offset
            self.delta = -self.delta
            tmp = self.axis0
            self.axis0 = self.axis1
            self.axis1 = tmp
            tmp = self.mirror0
            self.mirror0 = self.mirror1
            self.mirror1 = tmp
        if self.offset < 0.0:
            self.offset = -self.offset
            self.delta = -self.delta
            self.color = self.next_color
            self.next_color = self.pick_color()
            n = random.randrange(3)
            if n > 0:
                tmp = self.axis0
                self.axis0 = self.axis2
                self.axis2 = tmp
            if n < 2:
                self.mirror0 = not self.mirror0
