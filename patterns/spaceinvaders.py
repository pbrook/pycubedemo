# Copyright (C) John Leach <john@johnleach.co.uk>
# Released under the terms of the GNU General Public License version 3

import cubehelper
import numpy
import random


class Actor(object):
    def __init__(self, cube, *args):
        self.cube = cube
        self.set_position()
        self.set_colour()
        self.init()

    def set_colour(self, c=None):
        if c is None:
            c = cubehelper.random_color()
        self.colour = c

    def set_position(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

    def move_z(self, delta):
        self.z += delta
        if self.z < 0:
            self.z = 0
        if self.z > self.cube.size - 1:
            self.z = self.cube.size -1

    def centre_x(self):
        self.x = self.cube.size / 2

    def centre_y(self):
        self.y = self.cube.size / 2

    def centre_z(self):
        self.z = self.cube.size / 2

    def coords(self):
        return (self.x, self.y, self.z)

    def draw(self):
        self.cube.set_pixel(self.coords(), self.colour)

    def init(self):
        pass

    def tick(self):
        pass


class Player(Actor):
    def init(self):
        self.set_colour((0, 99, 0))
        self.centre_x()
        self.centre_y()
        self.z = 0


class Invader(Actor):
    def init(self):
        self.set_colour((255, 00, 00))
        self.x = random.randint(0, self.cube.size-1)
        self.y = random.randint(0, self.cube.size-1)
        self.z = self.cube.size-1
        self.speed = 5
        self.ticker = 0
        self.alive = True

    def tick(self):
        self.ticker += 1
        if self.ticker % self.speed == self.speed-1:
            if self.z == 0:
                self.alive = False
            self.move_z(-1)


class Pattern(object):
    def init(self):
        self.level = 10
        self.player = Player(self.cube)
        self.invader = Invader(self.cube)
        return 0.1

    def randomise_direction(self):
        self.direction = numpy.array([random.randint(0,1), random.randint(0, 1), random.randint(0,1)])
        for axis in range(0,3):
            if (self.position[axis] == self.cube.size-1):
                self.direction[axis] = 0
            if (self.position[axis] == 0):
                self.direction[axis] = 1

    def moveaxis(self,axis):
        if (self.direction[axis] == 1):
            self.position[axis] += 1
            if (self.position[axis] == self.cube.size-1):
                self.randomise_direction()
        else:
            self.position[axis] -= 1
            if (self.position[axis] == 0):
                self.randomise_direction()

    def tick(self):
        self.cube.clear()
        self.player.tick()
        self.invader.tick()
        self.player.draw()
        self.invader.draw()
        if not self.invader.alive:
            self.invader.init()
