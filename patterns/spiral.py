# A rotating spiral
# Copyright (C) Paul Brook <paul@nowt.org>
# Released under the terms of the GNU General Public License version 3

import cubehelper
import random
import math

FRAMERATE = 20

class Pattern(object):
    def init(self):
        self.double_buffer = True
        q0 = []
        q1 = []
        q2 = []
        q3 = []
        m = self.cube.size // 2
        for (x, y, z) in self.quadrant(m):
            q0.append((m + x, m + y, z))
            q1.append((m - (y + 1), m + x, z + 1.0))
            q2.append((m - (x + 1), m - (y + 1), z + 2.0))
            q3.append((m + y, m - (x + 1), z + 3.0))
        self.quad = q0 + q1 + q2 + q3
        self.z_offset = 0.0
        return 1.0 / FRAMERATE
    def quadrant(self, sz):
        r = float(sz) - 0.5
        prev = sz - 1
        for x in range(0, sz):
            xf = float(x) + 0.5
            yf = math.sqrt(r*r - xf*xf)
            y = int(yf)
            if y == prev:
                prev += 1
            for i in range(y, prev):
                z = math.atan2(i + 0.4, xf) * 2.0 / math.pi
                yield (x, i, z)
            prev = y
    def tick(self):
        self.cube.clear()
        color = 0xff0000
        zbase = self.z_offset
        while zbase < self.cube.size:
            for (x, y, z) in self.quad:
                z  += zbase
                if (z >= 0) and (z < self.cube.size):
                    self.cube.set_pixel((x, int(z), y), self.cube.plasma(z / 4.0))
            zbase += 4.0
        self.z_offset += 4.0 / FRAMERATE
        if self.z_offset > 0.0:
            self.z_offset -= 4.0
        raise StopIteration
