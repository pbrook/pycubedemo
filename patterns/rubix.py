# Bounce a pixel accross the cube in all three directions
# Copyright (C) Martyn Ranyard <martyn@ranyard.info>
# Released under the terms of the GNU General Public License version 3

import cubehelper
import random
import numpy
from copy import deepcopy

class Pattern(object):
    def rotateFrontFace(self):
        leftFaceTemp = deepcopy(self.leftFace)
        topFaceTemp = deepcopy(self.topFace)
        bottomFaceTemp = deepcopy(self.bottomFace)
        rightFaceTemp = deepcopy(self.rightFace)
        frontFaceTemp = deepcopy(self.frontFace)
        backFaceTemp = deepcopy(self.backFace)

        self.rotateFace(self.frontFace, frontFaceTemp)

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

        self.rotateFace(self.backFace, backFaceTemp)

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

        self.rotateFace(self.leftFace, leftFaceTemp)

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

        self.rotateFace(self.rightFace, rightFaceTemp)

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

        self.rotateFace(self.topFace, topFaceTemp)

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

        self.rotateFace(self.bottomFace, bottomFaceTemp)

        for a in range(3):
            self.backFace[a][0] = rightFaceTemp[a][0]
            self.rightFace[a][0] = frontFaceTemp[2-a][0]
            self.frontFace[a][0] = leftFaceTemp[a][0]
            self.leftFace[a][0] = backFaceTemp[2-a][0]

        self.setCube();

    def makeMove(self, move):
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

    def rotateFace(self, face, faceTemp):
        face[0][0] = faceTemp[0][2]
        face[0][1] = faceTemp[1][2]

        face[0][2] = faceTemp[2][2]
        face[1][2] = faceTemp[2][1]

        face[2][2] = faceTemp[2][0]
        face[2][1] = faceTemp[1][0]

        face[2][0] = faceTemp[0][0]
        face[1][0] = faceTemp[0][1]

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

            self.makeMove(move)

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

    def tick(self):
        self.cube.clear()

        self.oldCube = self.myCube[:]

        if self.time < self.numMoves:
            move = self.moves[self.time]

            self.makeMove(move)

        for a in range(8):
            for b in range(8):
                for c in range(8):
                    self.cube.set_pixel((a,b,c),self.myCube[a][b][c])

        self.time += 1
