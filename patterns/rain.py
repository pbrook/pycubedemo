# Swipe a plane across the cube in all 3 dimensions
# Copyright (C) Paul Brook <paul@nowt.org>
# Released under the terms of the GNU General Public License version 3

import random
import math
import cubehelper

class Drop(object):
    def __init__(self, cube, x, y):
        self.cube = cube
        self.x = x
        self.y = y
        self.z = -1
    def reset(self):
        self.z = self.cube.size
        self.speed = random.uniform(1.0, 0.25)
        self.color = cubehelper.random_color()
    def tick(self):
        self.z -= self.speed
        z0 = int(math.floor(self.z))
        if z0 < self.cube.size - 1:
            self.cube.set_pixel((self.x , self.y, z0 + 1), (0,0,0))
        if z0 >= 0:
            self.cube.set_pixel((self.x , self.y, z0), self.color)

class Pattern(object):
    def init(self):
        self.drops = []
        self.unused = []
        for x in range(0, self.cube.size):
            for y in range(0, self.cube.size):
                self.unused.append(Drop(self.cube, x, y))
        return 0.1
    def spawn(self):
        d = self.unused.pop(random.randrange(len(self.unused)))
        d.reset()
        self.drops.append(d)
    def tick(self):
        self.spawn()
        drops = self.drops;
        self.drops = []
        for d in drops:
            d.tick()
            if d.z < 0:
                self.unused.append(d)
            else:
                self.drops.append(d)
