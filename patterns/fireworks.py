# Fireworks
# Copyright (C) Paul Brook <paul@nowt.org>
# Released under the terms of the GNU General Public License version 3

import cubehelper
import random
import math

# Frame delta-time
DT = 1.0/8
GRAVITY = 1.0
FRICTION = 0.5
FADE = 0.5
# Detonation height
APEX = 0.8
# speed after detonation
FORCE = 3.0

class Voxel(object):
    def __init__(self, pos, v):
        self.pos = list(pos)
        self.v = list(v)

class Pattern(object):
    def init(self):
        self.double_buffer = True
        self.bits = None
        self.launch()
        return DT
    def tick(self):
        self.cube.clear()
        if self.bits is not None:
            self.descend()
        if self.rocket is not None:
            self.climb()
    def plot(self, voxel, color):
        sz = self.cube.size
        pos = voxel.pos
        x = int(pos[0] * sz - 0.001)
        y = int(pos[1] * sz - 0.001)
        z = int(pos[2] * sz - 0.001)
        self.cube.set_pixel((x, y, z), color)
    def spawn_bit(self, n):
        d = random.uniform(0.0, math.pi * 2.0)
        dz= random.uniform(-math.pi / 4, math.pi / 2)
        v0 = random.uniform(FORCE/2, FORCE)
        vx = v0 * math.sin(d) * math.cos(dz)
        vy = v0 * math.cos(d) * math.cos(dz)
        vz = v0 * math.sin(dz)
        return Voxel(self.rocket.pos, (vx, vy, vz))
    def explode(self):
        self.bit_color = cubehelper.random_color()
        self.bits = [self.spawn_bit(i) for i in range(0, 20)]
        self.fade = 1.0
        self.rocket = None
    def descend(self):
        color = cubehelper.mix_color((0.0,0.0,0.0), self.bit_color, self.fade)
        for bit in self.bits:
            pos = bit.pos
            v = bit.v
            v[0] *= FRICTION
            v[1] *= FRICTION
            v[2] *= FRICTION
            v[2] -= GRAVITY * DT
            for i in range(0, 3):
                pos[i] += v[i] * DT
                if pos[i] < 0.0:
                    pos[i] = 0.0
                    v[i] = 0
                elif pos[i] > 1.0:
                    pos[i] = 1.0
            self.plot(bit, color)
        self.fade -= FADE * DT
        if self.fade < 0.5 and self.rocket is None:
            self.launch()
        if self.fade <= 0:
            self.bits = None
    def launch(self):
        x = random.uniform(0.25, 0.75)
        y = random.uniform(0.25, 0.75)
        self.rocket = Voxel((x, y, 0.0), (0,0,0))
    def climb(self):
        self.plot(self.rocket, (1.0, 1.0, 1.0))
        z = self.rocket.pos[2]
        z += DT
        if z >= APEX:
            self.explode()
        else:
            self.rocket.pos[2] = z
