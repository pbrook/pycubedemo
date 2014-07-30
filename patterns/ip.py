# Display IP addresses
# Copyright (C) Paul Brook <paul@nowt.org>
# Released under the terms of the GNU General Public License version 3

import cubehelper
import font
import random
import math
import socket

COLORS = {' ':0x000000,'.':0xffffff,'0':0xffffff,'1':0xffffff,'2':0xff0000,'3':0x00ff00,'4':0x0000ff,'5':0xffff00,'6':0xff00ff,'7':0x00ffff,'8':0x00ffff,'9':0xff8000}

class Pattern(object):
    def init(self):
        self.message = self.get_ip()
        self.position = 0
        self.double_buffer = True
        return 0.35 / self.cube.size
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
            self.color = COLORS[c]
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

    def get_ip(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(('8.8.8.8', 80))
        name = sock.getsockname()[0]
        sock.close()
        return name