# LED cube serial driver
# Copyright (C) Paul Brook <paul@nowt.org>
# Released under the terms of the GNU General Public License version 3

import serial
import numpy
import cubehelper

def minicube_map(xyz):
    return (0, xyz[0] + xyz[1] * 4 + xyz[2] * 16)

def maxicube_map(xyz):
    (x, y, z) = xyz
    pos = 0
    board = y/4
    pos = x + (y % 4) * 8 + z * 16
    return (0, xyz[0] + xyz[1] * 4 + xyz[2] * 16)

class Cube(object):
    def __init__(self, args):
        self.ser = serial.Serial(args.port, 115200)
        self.current_board = None
        self.size = args.size
        if self.size == 4:
            self.mapfn = minicube_map
        elif self.size == 8:
            self.mapfn = maxicube_map
        else:
            raise Exception("Bad cube size: %d" % args.size)

    def do_cmd(self, cmd, d0, d1, d2):
        n = self.ser.write(bytearray((cmd, d0, d1, d2)))
        if n != 4:
            raise Exception("only wrote %d" % n)

    def bus_reset(self):
        self.do_cmd(0xff, 0xff, 0xff, 0xff)
        self.do_cmd(0xe0, 0xf0, 0xf1, 0xf2)
        self.current_board = None

    def select_board(self, board):
        self.bus_reset()
        self.do_cmd(0xe1, board, 0, 0)
        self.current_board = board

    def set_brightness(self, rgb):
        self.select_board(0xff)
        self.do_cmd(0xc0, rgb[0], rgb[1], rgb[2])

    def clear(self):
        self.select_board(0xff)
        for i in range(0, 128):
            self.do_cmd(i, 0, 0, 0)

    def set_pixel(self, xyz, rgb):
        (r, g, b) = cubehelper.color_to_int(rgb)
        (board, offset) = self.mapfn(xyz)
        if board != self.current_board:
            self.select_board(board)
        self.do_cmd(offset, r, g, b)

    def render(self):
        self.bus_reset()
