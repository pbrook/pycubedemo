# Creates a spiral based on a cosine wave through the cube
# Copyright (C) Martyn Ranyard <martyn@ranyard.info>
# Released under the terms of the GNU General Public License version 3

import cubehelper
import math

class Pattern(object):
    def init(self):
        self.counter = 0
        return 1.0 / self.cube.size
    def tick(self):
        if self.counter > (self.cube.size * self.cube.size):
            raise StopIteration;
        self.counter += 1;
        self.cube.clear()
# sine needs 0 to be midpoint... ah. but there's no midpoint
        for x in range(1, self.cube.size):
            y = math.cos(x+self.counter) * self.cube.size/2;
            y += self.cube.size/2
            z = math.cos(x+self.counter-1) * self.cube.size/2;
            z += self.cube.size/2
            color = cubehelper.random_color()
            self.cube.set_pixel([x,z,y],color);
