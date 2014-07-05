# Swipe a plane across the cube in all 3 dimensions
# Copyright (C) Paul Brook <paul@nowt.org>
# Released under the terms of the GNU General Public License version 3

import cubehelper

class Pattern(object):
    def init(self):
        self.level = 0.0
        self.delta = 1.0/16
        self.color = cubehelper.random_color()
        return 1.0/16
    def tick(self):
        color = cubehelper.scale_color(self.color, self.level)
        for x in range(0, self.cube.size):
            for y in range(0, self.cube.size):
                for z in range(0, self.cube.size):
                    self.cube.set_pixel((x, y, z), color)
        self.level += self.delta
        if self.level >= 1.0:
            self.delta = -self.delta
        if self.level <= 0:
            raise StopIteration

