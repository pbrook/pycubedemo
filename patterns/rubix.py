# Bounce a pixel accross the cube in all three directions
# Copyright (C) Martyn Ranyard <martyn@ranyard.info>
# Released under the terms of the GNU General Public License version 3

import cubehelper
import random
import numpy
from copy import deepcopy

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

        self.topFace = [[self.red for k in xrange(3)] for j in xrange(3)]
        self.bottomFace = [[self.green for k in xrange(3)] for j in xrange(3)]
        self.leftFace = [[self.orange for k in xrange(3)] for j in xrange(3)]
        self.rightFace = [[self.white for k in xrange(3)] for j in xrange(3)]
        self.frontFace = [[self.yellow for k in xrange(3)] for j in xrange(3)]
        self.backFace = [[self.blue for k in xrange(3)] for j in xrange(3)]

        # self.leftFace[0][0] = self.black;
        # self.topFace[0][0] = self.black;
        # self.bottomFace[0][0] = self.black;
        # self.rightFace[0][0] = self.black;
        # self.frontFace[0][0] = self.black;
        # self.backFace[0][0] = self.black;

        self.myCube = [[[self.black for k in xrange(self.n)] for j in xrange(self.n)] for i in xrange(self.n)]
        self.oldCube = [[[self.black for k in xrange(self.n)] for j in xrange(self.n)] for i in xrange(self.n)]

        self.setCube();

        self.moves = []

        self.numMoves = 20

        for x in range(self.numMoves):
            self.moves.append(random.randint(0,12))

        for move in reversed(self.moves):
            if move % 2 == 0:
                move += 1
            else:
                move -= 1

            if move == 0:
                self.rotateTopFace()
            elif move == 1:
                self.rotateTopFace()
                self.rotateTopFace()
                self.rotateTopFace()
            elif move == 2:
                self.rotateBottomFace()
            elif move == 3:
                self.rotateBottomFace()
                self.rotateBottomFace()
                self.rotateBottomFace()
            elif move == 4:
                self.rotateLeftFace()
            elif move == 5:
                self.rotateLeftFace()
                self.rotateLeftFace()
                self.rotateLeftFace()
            elif move == 6:
                self.rotateRightFace()
            elif move == 7:
                self.rotateRightFace()
                self.rotateRightFace()
                self.rotateRightFace()
            elif move == 8:
                self.rotateFrontFace()
            elif move == 9:
                self.rotateFrontFace()
                self.rotateFrontFace()
                self.rotateFrontFace()
            elif move == 10:
                self.rotateBackFace()
            elif move == 11:
                self.rotateBackFace()
                self.rotateBackFace()
                self.rotateBackFace()

        return 1.0 / 5

    def setCube(self):
        for a in range(3):
            for b in range(3):
                self.myCube[1 + (a*2)][1 + (b*2)][0] = self.bottomFace[a][b]
                self.myCube[1 + (a*2)][2 + (b*2)][0] = self.bottomFace[a][b]
                self.myCube[2 + (a*2)][1 + (b*2)][0] = self.bottomFace[a][b]
                self.myCube[2 + (a*2)][2 + (b*2)][0] = self.bottomFace[a][b]

                self.myCube[1 + (a*2)][1 + (b*2)][7] = self.topFace[a][b]
                self.myCube[1 + (a*2)][2 + (b*2)][7] = self.topFace[a][b]
                self.myCube[2 + (a*2)][1 + (b*2)][7] = self.topFace[a][b]
                self.myCube[2 + (a*2)][2 + (b*2)][7] = self.topFace[a][b]

                self.myCube[1 + (a*2)][0][1 + (b*2)] = self.rightFace[a][b]
                self.myCube[1 + (a*2)][0][2 + (b*2)] = self.rightFace[a][b]
                self.myCube[2 + (a*2)][0][1 + (b*2)] = self.rightFace[a][b]
                self.myCube[2 + (a*2)][0][2 + (b*2)] = self.rightFace[a][b]

                self.myCube[1 + (a*2)][7][1 + (b*2)] = self.leftFace[a][b]
                self.myCube[1 + (a*2)][7][2 + (b*2)] = self.leftFace[a][b]
                self.myCube[2 + (a*2)][7][1 + (b*2)] = self.leftFace[a][b]
                self.myCube[2 + (a*2)][7][2 + (b*2)] = self.leftFace[a][b]

                self.myCube[0][1 + (a*2)][1 + (b*2)] = self.frontFace[a][b]
                self.myCube[0][1 + (a*2)][2 + (b*2)] = self.frontFace[a][b]
                self.myCube[0][2 + (a*2)][1 + (b*2)] = self.frontFace[a][b]
                self.myCube[0][2 + (a*2)][2 + (b*2)] = self.frontFace[a][b]

                self.myCube[7][1 + (a*2)][1 + (b*2)] = self.backFace[a][b]
                self.myCube[7][1 + (a*2)][2 + (b*2)] = self.backFace[a][b]
                self.myCube[7][2 + (a*2)][1 + (b*2)] = self.backFace[a][b]
                self.myCube[7][2 + (a*2)][2 + (b*2)] = self.backFace[a][b]


    def rotateFrontFace(self):
        leftFaceTemp = deepcopy(self.leftFace)
        topFaceTemp = deepcopy(self.topFace)
        bottomFaceTemp = deepcopy(self.bottomFace)
        rightFaceTemp = deepcopy(self.rightFace)
        frontFaceTemp = deepcopy(self.frontFace)
        backFaceTemp = deepcopy(self.backFace)

        self.frontFace[0][0] = frontFaceTemp[0][2]
        self.frontFace[0][1] = frontFaceTemp[1][2]

        self.frontFace[0][2] = frontFaceTemp[2][2]
        self.frontFace[1][2] = frontFaceTemp[2][1]

        self.frontFace[2][2] = frontFaceTemp[2][0]
        self.frontFace[2][1] = frontFaceTemp[1][0]

        self.frontFace[2][0] = frontFaceTemp[0][0]
        self.frontFace[1][0] = frontFaceTemp[0][1]

        for a in range(3):
            self.leftFace[0][a] = bottomFaceTemp[0][a]
            self.bottomFace[0][a] = rightFaceTemp[0][2-a]
            self.rightFace[0][a] = topFaceTemp[0][a]
            self.topFace[0][a] = leftFaceTemp[0][2-a]

        self.setCube();

    def rotateBackFace(self):
        leftFaceTemp = deepcopy(self.leftFace)
        topFaceTemp = deepcopy(self.topFace)
        bottomFaceTemp = deepcopy(self.bottomFace)
        rightFaceTemp = deepcopy(self.rightFace)
        frontFaceTemp = deepcopy(self.frontFace)
        backFaceTemp = deepcopy(self.backFace)

        self.backFace[0][0] = backFaceTemp[0][2]
        self.backFace[0][1] = backFaceTemp[1][2]

        self.backFace[0][2] = backFaceTemp[2][2]
        self.backFace[1][2] = backFaceTemp[2][1]

        self.backFace[2][2] = backFaceTemp[2][0]
        self.backFace[2][1] = backFaceTemp[1][0]

        self.backFace[2][0] = backFaceTemp[0][0]
        self.backFace[1][0] = backFaceTemp[0][1]

        for a in range(3):
            self.leftFace[2][a] = bottomFaceTemp[2][a]
            self.bottomFace[2][a] = rightFaceTemp[2][2-a]
            self.rightFace[2][a] = topFaceTemp[2][a]
            self.topFace[2][a] = leftFaceTemp[2][2-a]

        self.setCube();

    def rotateLeftFace(self):
        leftFaceTemp = deepcopy(self.leftFace)
        topFaceTemp = deepcopy(self.topFace)
        bottomFaceTemp = deepcopy(self.bottomFace)
        rightFaceTemp = deepcopy(self.rightFace)
        frontFaceTemp = deepcopy(self.frontFace)
        backFaceTemp = deepcopy(self.backFace)

        self.leftFace[0][0] = leftFaceTemp[0][2]
        self.leftFace[0][1] = leftFaceTemp[1][2]

        self.leftFace[0][2] = leftFaceTemp[2][2]
        self.leftFace[1][2] = leftFaceTemp[2][1]

        self.leftFace[2][2] = leftFaceTemp[2][0]
        self.leftFace[2][1] = leftFaceTemp[1][0]

        self.leftFace[2][0] = leftFaceTemp[0][0]
        self.leftFace[1][0] = leftFaceTemp[0][1]

        for a in range(3):
            self.backFace[2][a] = bottomFaceTemp[a][2]
            self.bottomFace[a][2] = frontFaceTemp[2][2-a]
            self.frontFace[2][a] = topFaceTemp[a][2]
            self.topFace[a][2] = backFaceTemp[2][2-a]

        self.setCube();

    def rotateRightFace(self):
        leftFaceTemp = deepcopy(self.leftFace)
        topFaceTemp = deepcopy(self.topFace)
        bottomFaceTemp = deepcopy(self.bottomFace)
        rightFaceTemp = deepcopy(self.rightFace)
        frontFaceTemp = deepcopy(self.frontFace)
        backFaceTemp = deepcopy(self.backFace)

        self.rightFace[0][0] = rightFaceTemp[0][2]
        self.rightFace[0][1] = rightFaceTemp[1][2]

        self.rightFace[0][2] = rightFaceTemp[2][2]
        self.rightFace[1][2] = rightFaceTemp[2][1]

        self.rightFace[2][2] = rightFaceTemp[2][0]
        self.rightFace[2][1] = rightFaceTemp[1][0]

        self.rightFace[2][0] = rightFaceTemp[0][0]
        self.rightFace[1][0] = rightFaceTemp[0][1]

        for a in range(3):
            self.backFace[0][a] = bottomFaceTemp[a][0]
            self.bottomFace[a][0] = frontFaceTemp[0][2-a]
            self.frontFace[0][a] = topFaceTemp[a][0]
            self.topFace[a][0] = backFaceTemp[0][2-a]

        self.setCube();

    def rotateTopFace(self):
        leftFaceTemp = deepcopy(self.leftFace)
        topFaceTemp = deepcopy(self.topFace)
        bottomFaceTemp = deepcopy(self.bottomFace)
        rightFaceTemp = deepcopy(self.rightFace)
        frontFaceTemp = deepcopy(self.frontFace)
        backFaceTemp = deepcopy(self.backFace)

        self.topFace[0][0] = topFaceTemp[0][2]
        self.topFace[0][1] = topFaceTemp[1][2]

        self.topFace[0][2] = topFaceTemp[2][2]
        self.topFace[1][2] = topFaceTemp[2][1]

        self.topFace[2][2] = topFaceTemp[2][0]
        self.topFace[2][1] = topFaceTemp[1][0]

        self.topFace[2][0] = topFaceTemp[0][0]
        self.topFace[1][0] = topFaceTemp[0][1]

        for a in range(3):
            self.backFace[a][2] = rightFaceTemp[a][2]
            self.rightFace[a][2] = frontFaceTemp[2-a][2]
            self.frontFace[a][2] = leftFaceTemp[a][2]
            self.leftFace[a][2] = backFaceTemp[2-a][2]

        self.setCube();

    def rotateBottomFace(self):
        leftFaceTemp = deepcopy(self.leftFace)
        topFaceTemp = deepcopy(self.topFace)
        bottomFaceTemp = deepcopy(self.bottomFace)
        rightFaceTemp = deepcopy(self.rightFace)
        frontFaceTemp = deepcopy(self.frontFace)
        backFaceTemp = deepcopy(self.backFace)

        self.bottomFace[0][0] = bottomFaceTemp[0][2]
        self.bottomFace[0][1] = bottomFaceTemp[1][2]

        self.bottomFace[0][2] = bottomFaceTemp[2][2]
        self.bottomFace[1][2] = bottomFaceTemp[2][1]

        self.bottomFace[2][2] = bottomFaceTemp[2][0]
        self.bottomFace[2][1] = bottomFaceTemp[1][0]

        self.bottomFace[2][0] = bottomFaceTemp[0][0]
        self.bottomFace[1][0] = bottomFaceTemp[0][1]

        for a in range(3):
            self.backFace[a][0] = rightFaceTemp[a][0]
            self.rightFace[a][0] = frontFaceTemp[2-a][0]
            self.frontFace[a][0] = leftFaceTemp[a][0]
            self.leftFace[a][0] = backFaceTemp[2-a][0]

        self.setCube();

    def tick(self):
        self.cube.clear()

        self.oldCube = self.myCube[:]

        if self.time < self.numMoves:
            move = self.moves[self.time]

            if move == 0:
                self.rotateTopFace()
            elif move == 1:
                self.rotateTopFace()
                self.rotateTopFace()
                self.rotateTopFace()
            elif move == 2:
                self.rotateBottomFace()
            elif move == 3:
                self.rotateBottomFace()
                self.rotateBottomFace()
                self.rotateBottomFace()
            elif move == 4:
                self.rotateLeftFace()
            elif move == 5:
                self.rotateLeftFace()
                self.rotateLeftFace()
                self.rotateLeftFace()
            elif move == 6:
                self.rotateRightFace()
            elif move == 7:
                self.rotateRightFace()
                self.rotateRightFace()
                self.rotateRightFace()
            elif move == 8:
                self.rotateFrontFace()
            elif move == 9:
                self.rotateFrontFace()
                self.rotateFrontFace()
                self.rotateFrontFace()
            elif move == 10:
                self.rotateBackFace()
            elif move == 11:
                self.rotateBackFace()
                self.rotateBackFace()
                self.rotateBackFace()

        for a in range(8):
            for b in range(8):
                for c in range(8):
                    self.cube.set_pixel((a,b,c),self.myCube[a][b][c])

        self.time += 1
