# Fill the cube with a solid colour, starting from random corners
# Copyright (C) Alex Silcock <alex@alexsilcock.net>
# Released under the terms of the GNU General Public License version 3

import cubehelper
import math
import random

class Pattern(object):
    def init(self):
        self.filling_color = cubehelper.random_color()
        self.offset = 0 # how far from the corner to draw
        self.double_buffered = True
        # Vertices:
        # bottom layer
        # 2--6
        # |  |
        # 0--4
        #
        # top layer
        # 3--7
        # |  |
        # 1--5

        cs = self.cube.size-1

        self.corners = [
            [(0, 0, 0), (1, 1, 1)],       # 0
            [(0, 0, cs), (1, 1, -1)],     # 1
            [(0, cs, 0), (1, -1, 1)],     # 2
            [(0, cs, cs), (1, -1, -1)],   # 3
            [(cs, 0, 0), (-1, 1, 1)],     # 4
            [(cs, 0, cs), (-1, 1, -1)],   # 5
            [(cs, cs, 0), (-1, -1, 1)],   # 6
            [(cs, cs, cs), (-1, -1, -1)], # 7
        ]

        self.black = (0.0, 0.0, 0.0)

        self.corner = self.corners[random.randrange(0, 8)] # the current corner we're filling from

        return 0.6 / self.cube.size

    def tick(self):
        if (self.offset < self.cube.size):
            self.draw_cubeface(self.corner, self.offset, self.filling_color)


        # now cover it over with black
        o = self.offset - 5
        if o >= 0:
            self.draw_cubeface(self.corner, o, self.black)

        if o == self.cube.size-1:
            self.offset = 0
            self.corner = self.corners[random.randrange(0, 8)]
            self.filling_color = cubehelper.random_color(self.filling_color)
            raise StopIteration
        else:
            self.offset += 1

    def draw_cubeface(self, corner, offset, color):
        o = offset
        c = corner[0]
        d = corner[1]

        corner1 = (c[0] + d[0]*o, c[1] + d[1]*o, c[2] + d[2]*o)

        # draw yz plane
        corner2 = (c[0] + d[0]*o, c[1], c[2])
        for coord in self.plane(corner1, corner2):
            self.cube.set_pixel(coord, color)

        # draw xz plane
        corner2 = (c[0], c[1] + d[1]*o, c[2])
        for coord in self.plane(corner1, corner2):
            self.cube.set_pixel(coord, color)

        # draw xy plane
        corner2 = (c[0], c[1], c[2] + d[2]*o)
        for coord in self.plane(corner1, corner2):
            self.cube.set_pixel(coord, color)

    def plane(self, corner1, corner2):
        """Get the points inside the specified plane"""
        (x1, y1, z1) = corner1
        (x2, y2, z2) = corner2

        # figure out which plane the points are on
        if x1==x2:
            # yz plane
            for y in self.range_incl(y1, y2):
                for z in self.range_incl(z1, z2):
                    yield (x1, y, z)

        if y1==y2:
            # xz plane
            for x in self.range_incl(x1, x2):
                for z in self.range_incl(z1, z2):
                    yield (x, y1, z)

        if z1==z2:
            # xy plane
            for y in self.range_incl(y1, y2):
                for x in self.range_incl(x1, x2):
                    yield (x, y, z1)

    def range_incl(self, start, end):
        """Like the range function, but it can work in reverse, and it includes the end value"""
        if end >= start:
            return range(start, end+1)
        elif end < start:
            return range(start, end-1, -1)
