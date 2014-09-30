# Plasma
# Copyright (C) Paul Brook <paul@nowt.org>
# Released under the terms of the GNU General Public License version 3

import random
import cubehelper
import math

DT = 0.05

def color_from_val(val):
    if val < 85:
        r = val * 3;
        g = 255 - r;
        b = 0;
    elif val < 170:
        b = (val - 85) * 3;
        r = 255 - b;
        g = 0;
    else:
        g = (val - 170) * 3;
        b = 255 - g;
        r = 0;
    return (r, g, b)

class Pattern(object):
    def init(self):
        self.offset = 0.0
        return DT

    def tick(self):
        self.offset -= DT / 1.0
        if self.offset < 0:
            self.offset += 1.0
            raise StopIteration
        sz = self.cube.size
        scale = math.pi * 2.0 / float(sz)
        offset = 0.5
        for y in range(0, sz):
            for z in range(0, sz):
                for x in range(0, sz):
                    u = math.cos((x + offset) * scale)
                    v = math.cos((y + offset) * scale)
                    w = math.cos((z + offset) * scale)
                    e = (u + v + w + 3.0) / 6.0
                    color = self.cube.plasma(self.offset + e)
                    self.cube.set_pixel((x, y, z), color)
