# Scroll a message round the cube
# Copyright (C) Paul Brook <paul@nowt.org>
# Released under the terms of the GNU General Public License version 3

import cubehelper
import font
import random
import math

def walker(cube):
    sz = cube.size - 1
    for y in range(sz, 0, -1):
        yield (0, y)
    for x in range(0, sz):
        yield (x, 0)
    for y in range(0, cube.size):
        yield (sz, y)

class Pattern(object):
    def init(self):
        self.saved_message = 'Leeds Hackspace'
        self.position = 0
        self.double_buffer = True
        self.pos = [pos for pos in walker(self.cube)]
        self.reset()
        return 0.5 / self.cube.size
    def reset(self):
        self.bitmap = [0] * len(self.pos)
        self.message = self.saved_message
        self.color = cubehelper.random_color()
    def tick(self):
        self.cube.clear()
        while len(self.bitmap) < len(self.pos):
            if self.message == '':
                break;
            c = self.message[0]
            self.message = self.message[1:]
            n = ord(c) - 32
            if n >= 0 and n < len(font.font_data):
                self.bitmap.extend(font.font_data[n])
            self.bitmap.append(0)
        if len(self.bitmap) == 0:
            self.reset()
            raise StopIteration
        for i in range(0, min(len(self.bitmap), len(self.pos))):
            mask = self.bitmap[i]
            (x, y) = self.pos[i]
            for z in range(0, 8):
                if mask & (0x80 >> z):
                    color = self.color
                else:
                    color = (0,0,0)
                self.cube.set_pixel((x, y, z), color)
        self.bitmap.pop(0)
