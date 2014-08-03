# Fork of rain - pastel "snow flakes" slowly falling (interpolated)
# Copyright (C) Paul Brook <paul@nowt.org>
# Released under the terms of the GNU General Public License version 3

import random
import math
import cubehelper

BLACK = (0,0,0)
WHITE = (255,255,255)

FRAME_RATE = 25
FRAME_TIME = 1.0 / FRAME_RATE
SPAWN_PROBABILITY = 5.0 / FRAME_RATE

class Drop(object):
    def __init__(self, cube, x, y):
        self.cube = cube
        self.x = x
        self.y = y
        self.z = -1
    def reset(self):
        self.z = self.cube.size
        self.speed = random.uniform(1, 2)
        self.color = cubehelper.mix_color(cubehelper.random_color(), WHITE, 0.7)
    def tick(self):
        self.z -= self.speed * FRAME_TIME
        if self.z >= 0:
            self.set_pixel_interpolate_float_z(self.x, self.y, self.z, self.color)
    # TODO: generalize interpolation, place in cubehelper
    # assumes z > 0
    def set_pixel_interpolate_float_z(self, x, y, z, color):
        # we're always on a pixel, or between two
        if float(int(z)) == z: # on pixel
            self.cube.set_pixel((x, y, int(z)), color)
        else: # between
            z0 = int(math.floor(z))
            z1 = int(math.floor(z+1))
            z1_strength = z - z0
            z0_strength = 1 - z1_strength

            self.cube.set_pixel((x, y, z0), cubehelper.mix_color(BLACK, color, z0_strength))
            self.cube.set_pixel((x, y, z1), cubehelper.mix_color(BLACK, color, z1_strength))

class Pattern(object):
    def init(self):
        self.double_buffer = True
        self.drops = []
        self.unused = []
        for x in range(0, self.cube.size):
            for y in range(0, self.cube.size):
                self.unused.append(Drop(self.cube, x, y))
        return FRAME_TIME
    def spawn(self):
        d = self.unused.pop(random.randrange(len(self.unused)))
        d.reset()
        self.drops.append(d)
    def tick(self):
        if random.random() < SPAWN_PROBABILITY:
            self.spawn()
        drops = self.drops;
        self.drops = []
        self.cube.clear()
        for d in drops:
            d.tick()
            if d.z < 0:
                self.unused.append(d)
            else:
                self.drops.append(d)
