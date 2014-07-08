# Display message a character at a time
# Copyright (C) Paul Brook <paul@nowt.org>
# Released under the terms of the GNU General Public License version 3

import cubehelper
import font
import random
import math

class Pattern(object):
    def init(self):
        self.message = 'Hello World'
        self.position = 0
        self.double_buffer = True
        return 0.5 / self.cube.size
    def tick(self):
        self.cube.clear()
        if self.position == 0:
            if self.message == '':
                raise StopIteration
            c = self.message[0]
            self.message = self.message[1:]
            n = ord(c) - 32
            if n >= 0 and n < len(font.font_data):
                self.data = font.font_data[n]
            else:
                self.data = ()
            self.color = cubehelper.random_color()
        x = (self.cube.size - len(self.data)) / 2
        y = self.position
        for mask in self.data:
            for z in range(0, 8):
                if mask & (0x80 >> z):
                    color = self.color
                else:
                    color = (0,0,0)
                self.cube.set_pixel((x, y, z), color)
            x += 1
        self.position += 1
        if self.position == self.cube.size:
            self.position = 0
