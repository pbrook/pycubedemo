# Swipe a line across the cube in all 3 dimensions
# Copyright (C) Martyn Ranyard <martyn@ranyard.info>
# Released under the terms of the GNU General Public License version 3

import cubehelper
import random

class Pattern(object):
    def init(self):
        self.color = cubehelper.random_color()
        self.point0 = [random.randint(0,self.cube.size-1),random.randint(0,self.cube.size-1),random.randint(0,self.cube.size-1)]
        self.point1 = [random.randint(0,self.cube.size-1),random.randint(0,self.cube.size-1),random.randint(0,self.cube.size-1)]
        self.direction0 = self.newdirection(self.point0)
        self.direction1 = self.newdirection(self.point1)
        return 2.5 / self.cube.size
    def newdirection(self,point):
        going = [0,0,0]
        axisint = 0
        for axis in point:
            if axis <= 0:
                going[axisint] = 1;
            elif axis >= self.cube.size-1:
                going[axisint] = -1;
            else:
                if random.randint(0,1) == 1:
                    going[axisint] = 1
                else:
                    going[axisint] = -1
            axisint += 1
        return going
    def hitedge(self,point):
        print(point)
        for axis in point:
            print(axis)
            if (axis == 0) or (axis == self.cube.size-1):
                return True
        return False
    def tick(self):
        if self.hitedge(self.point0):
            self.direction0 = self.newdirection(self.point0)
            print('Hit Edge, new direction, point 0 - ',self.direction0)
        if self.hitedge(self.point1):
            self.direction1 = self.newdirection(self.point1)
            print('Hit Edge, new direction, point 1 - ',self.direction1)
        for i in range(0,3):
            self.point0[i] += self.direction0[i]
            self.point1[i] += self.direction1[i]
        self.cube.clear()
        print('From ',self.point0,' to ',self.point1)
        for point in cubehelper.line(self.point0,self.point1):
            print(point)
            self.cube.set_pixel(point,self.color)
