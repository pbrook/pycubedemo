# Zoom a wireframe cube in and out of the centre
# Copyright (C) Alex Silcock <alex@alexsilcock.net>
# Released under the terms of the GNU General Public License version 3

import cubehelper
import math

class Pattern(object):
    def init(self):
        self.direction = 1 # 1=shrink, -1=expand
        self.current_size = 0 # size is distance from edge of cube, not distance from centre
        self.max_size = (self.cube.size - 1) / 2
        self.color = cubehelper.random_color()
        self.double_buffer = True
        return 1.0 / self.cube.size
        
    def tick(self):
        # Draw the cube at its current size, then reduce the size for the next iteration
        self.cube.clear()
        self.draw_cube(self.current_size, self.color)

        self.current_size += self.direction
        if self.current_size == 0:
            self.direction *= -1
        elif self.current_size == self.max_size:
            self.direction *= -1
            self.color = cubehelper.random_color(self.color)

    def draw_cube(self, edge_offset, color):
        left = edge_offset
        right = (self.cube.size - 1) - left

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

        vertices = [
            (left, left, left),   # 0
            (left, left, right),  # 1
            (left, right, left),  # 2
            (left, right, right), # 3
            (right, left, left),  # 4
            (right, left, right), # 5
            (right, right, left), # 6
            (right, right, right) # 7
        ]

        lines = [(2, 6), (2, 0), (0, 4), (4, 6), (3, 7), (3, 1), (1, 5), (5, 7), (2, 3), (0, 1), (4, 5), (6, 7)]

        for (i, j) in lines:
            for coord in cubehelper.line(vertices[i], vertices[j]):
                self.cube.set_pixel(coord, color)
