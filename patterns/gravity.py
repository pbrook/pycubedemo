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

GRAVITY = 10.0
COEFFICIENT_OF_RESTITUTION = 0.9

class Drop(object):
    def __init__(self, cube, x, y):
        self.cube = cube
        self.x = x
        self.y = y
        self.z = -10
    def reset(self):
        self.z = self.cube.size
        self.speed = 0; #random.uniform(1, 2)
        self.color = cubehelper.mix_color(cubehelper.random_color(), WHITE, 0.4)
    def tick(self):
        self.speed += GRAVITY * FRAME_TIME
        self.z -= (self.speed) * FRAME_TIME
        # apply bounce
        # make sure there's still enough energy left not to sit on bottom
        # if there's not gravity will suck them down to be cleaned up
        if self.z < 0 and self.speed > GRAVITY:
            self.speed = -self.speed * COEFFICIENT_OF_RESTITUTION

        position_float = (self.x,self.y,self.z)
        pixels = cubehelper.sanitized_interpolated(position_float, self.color, self.cube.size)
        self.cube.set_pixels(pixels)

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
        try:
            d = self.unused.pop(random.randrange(len(self.unused)))
            d.reset()
            self.drops.append(d)
        except ValueError:
            pass
    def tick(self):
        if random.random() < SPAWN_PROBABILITY:
            self.spawn()
        drops = self.drops;
        self.drops = []
        self.cube.clear()
        for d in drops:
            d.tick()
            if d.z < -5:
                self.unused.append(d)
            else:
                self.drops.append(d)
