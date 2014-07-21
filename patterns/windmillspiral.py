# Swipe a line across the cube in all 3 dimensions
# Copyright (C) Martyn Ranyard <martyn@ranyard.info>
# Released under the terms of the GNU General Public License version 3

import cubehelper
import random
import math

STEP = 0.3

class Pattern(object):
    def init(self):
        self.xrot = [0,1,2,3,4,5,6,7]
        self.switched = False
        self.double_buffer = True
        return 2.5 * STEP / (self.cube.size -1)
    def tick(self):
        self.cube.clear()
        for plane in range(0,self.cube.size):
            sz = self.cube.size -1
            if self.xrot[plane] < 0:
                self.xrot[plane] += sz
            i = self.xrot[plane]
            fade = plane/(self.cube.size-1.0)
            fade = 1-math.cos(fade*math.pi/2.0)
            color = cubehelper.mix_color(0xff0000,0x0000ff,fade)
            for point in cubehelper.line((i,plane,0),(sz-i,plane,sz)):
                self.cube.set_pixel(point,color)
            for point in cubehelper.line((0,plane,sz-i),(sz,plane,i)):
                self.cube.set_pixel(point,color)
            self.xrot[plane] -= STEP
