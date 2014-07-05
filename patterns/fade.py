# Swipe a plane across the cube in all 3 dimensions
# Copyright (C) Paul Brook <paul@nowt.org>
# Released under the terms of the GNU General Public License version 3

class Pattern(object):
    def init(self):
        self.level = 0.0
        self.delta = 1.0/16
        return 1.0/16
    def tick(self):
        color = tuple([self.level]*3)
        for x in range(0, self.cube.size):
            for y in range(0, self.cube.size):
                for z in range(0, self.cube.size):
                    self.cube.set_pixel((x, y, z), color)
        self.level += self.delta
        if self.level >= 1.0:
            self.delta = -self.delta
        if self.level <= 0:
            raise StopIteration

