# Plasma
# Copyright (C) Paul Brook <paul@nowt.org>
# Released under the terms of the GNU General Public License version 3

import random
import cubehelper
import math

DT = 1.0/20
FADE_TIME = 5.0
ACTIVE_TIME = 5.0

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
        self.fade_distance = 0.0
        self.timer = 0.0
        return DT

    def tick(self):
        self.timer += DT
        self.offset -= DT / 1.0
        if self.offset < 0:
            self.offset += 1.0
        sz = self.cube.size
        scale = math.pi * 2.0 / float(sz)
        offset = 0.5
        if self.timer < FADE_TIME:
            self.fade_distance += DT * 11.0 / FADE_TIME
        elif self.timer > FADE_TIME + ACTIVE_TIME:
            self.fade_distance -= DT * 11.0 / FADE_TIME

        for y in range(0, sz):
            for z in range(0, sz):
                for x in range(0, sz):
                    u = math.cos((x + offset) * scale)
                    v = math.cos((y + offset) * scale)
                    w = math.cos((z + offset) * scale)
                    e = (u + v + w + 3.0) / 6.0
                    color = self.cube.plasma(self.offset + e)
                    dist = abs(x - 3.5) + abs(y - 3.5) + abs(z - 3.5)
                    delta = dist - self.fade_distance
                    if delta > 0.0:
                        if delta > 1.0:
                            color = 0
                        else:
                            color = cubehelper.mix_color(color, 0, delta)
                    self.cube.set_pixel((x, y, z), color)
        if self.timer > FADE_TIME * 2.0 + ACTIVE_TIME:
            raise StopIteration
