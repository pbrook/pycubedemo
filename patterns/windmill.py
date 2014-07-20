# Swipe a line across the cube in all 3 dimensions
# Copyright (C) Martyn Ranyard <martyn@ranyard.info>
# Released under the terms of the GNU General Public License version 3

import cubehelper
import random

class Pattern(object):
    def init(self):
        self.xrot = 0
        self.yrot = 0
        self.switched = False
        return 2.5 / self.cube.size
    def tick(self):
        self.cube.clear()
        if self.xrot == self.cube.size-1:
            self.xrot = 0
        sz = self.cube.size -1
        i = self.xrot
        for point in cubehelper.line((i,0,0),(sz-i,0,sz)):
            self.cube.set_pixel(point,0xffffff)
        for point in cubehelper.line((0,0,sz-i),(sz,0,i)):
            self.cube.set_pixel(point,0xffffff)
        self.xrot += 1
