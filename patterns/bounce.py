# Bounce a pixel accross the cube in all three directions
# Copyright (C) Martyn Ranyard <martyn@ranyard.info>
# Released under the terms of the GNU General Public License version 3

import cubehelper
import random
import numpy

class Pattern(object):
    def init(self):
        self.double_buffer = True

        self.time = 0;

        self.white = (255,255,255)
        self.red = (255,0,0)
        self.yellow = (255,255,0)
        self.green = (0,128,0)
        self.blue = (0,0,255)
        self.orange = (255,165,0)
        self.black = (0,0,0)

        self.n = 8

        self.topFace = [[self.red]*3]*3
        self.bottomFace = [[self.green]*3]*3
        self.leftFace = [[self.orange]*3]*3
        self.rightFace = [[self.yellow]*3]*3
        self.frontFace = [[self.white]*3]*3
        self.backFace = [[self.blue]*3]*3

        self.myCube = [[[self.black for k in xrange(self.n)] for j in xrange(self.n)] for i in xrange(self.n)]
        self.oldCube = [[[self.black for k in xrange(self.n)] for j in xrange(self.n)] for i in xrange(self.n)]

        for a in range(3):
            for b in range(3):
                self.myCube[1 + (a*2)][1 + (b*2)][0] = self.bottomFace[a][b]
                self.myCube[1 + (a*2)][2 + (b*2)][0] = self.bottomFace[a][b]
                self.myCube[2 + (a*2)][1 + (b*2)][0] = self.bottomFace[a][b]
                self.myCube[2 + (a*2)][2 + (b*2)][0] = self.bottomFace[a][b]
        for a in range(3):
            for b in range(3):
                self.myCube[1 + (a*2)][1 + (b*2)][7] = self.topFace[a][b]
                self.myCube[1 + (a*2)][2 + (b*2)][7] = self.topFace[a][b]
                self.myCube[2 + (a*2)][1 + (b*2)][7] = self.topFace[a][b]
                self.myCube[2 + (a*2)][2 + (b*2)][7] = self.topFace[a][b]

        for a in range(3):
            for b in range(3):
                self.myCube[1 + (a*2)][0][1 + (b*2)] = self.leftFace[a][b]
                self.myCube[1 + (a*2)][0][2 + (b*2)] = self.leftFace[a][b]
                self.myCube[2 + (a*2)][0][1 + (b*2)] = self.leftFace[a][b]
                self.myCube[2 + (a*2)][0][2 + (b*2)] = self.leftFace[a][b]
        for a in range(3):
            for b in range(3):
                self.myCube[1 + (a*2)][7][1 + (b*2)] = self.rightFace[a][b]
                self.myCube[1 + (a*2)][7][2 + (b*2)] = self.rightFace[a][b]
                self.myCube[2 + (a*2)][7][1 + (b*2)] = self.rightFace[a][b]
                self.myCube[2 + (a*2)][7][2 + (b*2)] = self.rightFace[a][b]

        for a in range(3):
            for b in range(3):
                self.myCube[0][1 + (a*2)][1 + (b*2)] = self.frontFace[a][b]
                self.myCube[0][1 + (a*2)][2 + (b*2)] = self.frontFace[a][b]
                self.myCube[0][2 + (a*2)][1 + (b*2)] = self.frontFace[a][b]
                self.myCube[0][2 + (a*2)][2 + (b*2)] = self.frontFace[a][b]
        for a in range(3):
            for b in range(3):
                self.myCube[7][1 + (a*2)][1 + (b*2)] = self.backFace[a][b]
                self.myCube[7][1 + (a*2)][2 + (b*2)] = self.backFace[a][b]
                self.myCube[7][2 + (a*2)][1 + (b*2)] = self.backFace[a][b]
                self.myCube[7][2 + (a*2)][2 + (b*2)] = self.backFace[a][b]

        return 1.0 / 20

    def rotateFrontFace(self):
        for a in range(7):
            self.myCube[1][a][0] = self.oldCube[1][a+1][0]
            self.myCube[2][a][0] = self.oldCube[2][a+1][0]

            self.myCube[1][7][a] = self.oldCube[1][7][a+1]
            self.myCube[2][7][a] = self.oldCube[2][7][a+1]

            b = 6-a
            self.myCube[1][b+1][7] = self.oldCube[1][b][7]
            self.myCube[2][b+1][7] = self.oldCube[2][b][7]

            self.myCube[1][0][b+1] = self.oldCube[1][0][b]
            self.myCube[2][0][b+1] = self.oldCube[2][0][b]


    def tick(self):
        self.cube.clear()

        self.time += 1

        self.oldCube = self.myCube[:]

        if self.time < 999:
            self.rotateFrontFace()
        #
        # print(self.myCube[1][1][0])
        # print(self.oldCube[1][1][0])

        for a in range(8):
            for b in range(8):
                for c in range(8):
                    self.cube.set_pixel((a,b,c),self.myCube[a][b][c])
