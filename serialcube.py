# LED cube serial driver
# Copyright (C) Paul Brook <paul@nowt.org>
# Released under the terms of the GNU General Public License version 3

import numpy
import cubehelper
import socket

class TCPWriter(object):
    def __init__(self, addr):
        (host, port) = addr.split(':')
        port = int(port)
        if host == "":
            host = "localhost"
        self.sock = socket.create_connection((host, int(port)))
    def write(self, b):
        self.sock.sendall(b)

def FileWriter(name):
    return open(name, "wb")

def SerialWriter(port):
    import serial
    return serial.Serial(port, 115200)

class SPIWriter(object):
    def __init__(self, port):
        import spidev
        if port[:11] == '/dev/spidev':
            port = port[11:]
        bus = None
        for sep in '.,:-':
            if sep in port:
                p = port.split(sep)
                bus = int(p[0])
                dev = int(p[1])
                break
        if bus is None:
            if port == '':
                bus = 1
            else:
                bus = int(port)
            dev = 0
        print((bus, dev))
        spi = spidev.SpiDev(bus, dev)
        spi.max_speed_hz = 2000000
        spi.mode = 3
        spi.lsbfirst = False
        spi.cshigh = False
        spi.bits_per_word = 8
        self.spi = spi
    def write(self, b):
        self.spi.writebytes(list(b))


def minicube_map(xyz):
    return (0, xyz[0] + xyz[1] * 4 + xyz[2] * 16)

def maxicube_map(xyz):
    (x, y, z) = xyz
    pos = 0
    board = y//2
    pos = x + ((y ^ 1) % 2) * 8 + (z ^ 1) * 16
    return (board, pos)

class Cube(object):
    def __init__(self, args):
        writers = {'tcp':TCPWriter, 'file':FileWriter, 'serial':SerialWriter, 'spi':SPIWriter}
        if ':' in args.port:
            (proto, port) = args.port.split(':', 1)
        else:
            proto = ''
        if proto not in writers:
            port = args.port
            if ':' in port:
                proto = 'tcp'
            elif port[:8] == '/dev/tty':
                proto = 'serial'
            elif port[:8] == '/dev/spi':
                proto = 'spi'
            elif port[0] == '@':
                proto = 'file'
                port = port[1:]
            else:
                proto = 'file'
        self.ser = writers[proto](port)
        self.current_board = None
        self.size = args.size
        self.write_page = 0
        self.display_page = 0
        if self.size == 4:
            self.mapfn = minicube_map
            self.color = False
        elif self.size == 8:
            self.mapfn = maxicube_map
            self.color = True
        else:
            raise Exception("Bad cube size: %d" % args.size)

    def do_cmd(self, cmd, d0, d1, d2):
        self.ser.write(bytearray((cmd, d0, d1, d2)))

    def bus_reset(self):
        self.do_cmd(0xff, 0xff, 0xff, 0xff)
        self.do_cmd(0xe0, 0xf0, 0xf1, 0xf2)
        self.current_board = None

    def select_board(self, board = 0xff):
        self.bus_reset()
        self.do_cmd(0xe1, board, 0, 0)
        self.current_board = board

    def set_brightness(self, rgb):
        self.select_board()
        self.do_cmd(0xc0, rgb[0], rgb[1], rgb[2])

    def clear(self):
        self.select_board()
        for i in range(0, 128):
            self.do_cmd(i, 0, 0, 0)

    def _flip(self):
        self.select_board()
        self.do_cmd(0x80, 0, self.display_page, self.write_page)

    def single_buffer(self):
        self.write_page = self.display_page
        self._flip()

    def swap(self):
        self.display_page = self.write_page
        self.write_page = 1 - self.write_page
        self._flip()

    def set_pixel(self, xyz, rgb):
        (r, g, b) = cubehelper.color_to_int(rgb)
        (board, offset) = self.mapfn(xyz)
        if board != self.current_board:
            self.select_board(board)
        self.do_cmd(offset, r, g, b)

    def render(self):
        self.bus_reset()
