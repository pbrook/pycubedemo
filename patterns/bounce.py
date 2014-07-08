# Bounce a pixel accross the cube in all three directions
# Copyright (C) Martyn Ranyard <martyn@ranyard.info>
# Released under the terms of the GNU General Public License version 3

import cubehelper
import random
import numpy

class Pattern(object):
    def init(self):
        self.position = numpy.array([random.randint(1,self.cube.size)-1, random.randint(1,self.cube.size)-1, random.randint(1,self.cube.size)-1])
        self.randomise_direction()
        return 1.0 / self.cube.size
    def randomise_direction(self):
        self.direction = numpy.array([random.randint(0,1),random.randint(0,1),random.randint(0,1)])
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
        for axis in range(0,random.randint(1,3)):
            self.moveaxis(axis)
        self.cube.set_pixel((self.position[0],self.position[1],self.position[2]),cubehelper.random_color())
