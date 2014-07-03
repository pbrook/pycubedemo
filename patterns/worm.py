# Worm
# Copyright (C) Paul Brook <paul@nowt.org>
# Released under the terms of the GNU General Public License version 3

import random

IQ = 10

INITIAL_ENERGY = 1.0
ENERGY_DECAY = 0.1

def color_for_energy(e):
    return (e, e, e)

class Pattern(object):
    def init(self):
        self.body = []
        self.energy = []
        self.heading = 0
        self.tries = 0
        i = self.cube.size / 2
        self.current_pos = (i, i, i)
        self.forward = 1
        self.blocked = True
        return 0.1

    def is_empty(self, pos):
        if min(pos) < 0 or max(pos) >= self.cube.size:
            return False
        return pos not in self.body

    def push(self, pos):
        self.body.append(pos)
        self.energy.append(INITIAL_ENERGY)

    def advance(self):
        newpos = list(self.current_pos)
        newpos[self.heading] += self.forward
        return tuple(newpos)

    def age(self):
        for i in range(0, len(self.energy)):
            e = self.energy[i] - ENERGY_DECAY
            pos = self.body[i]
            self.energy[i] = e
            if e > 0:
                color = color_for_energy(e)
            else:
                color = (0, 0, 0)
            self.cube.set_pixel(pos, color)
        while self.energy[0] <= 0:
            self.energy.pop(0)
            self.body.pop(0)

    def tick(self):
        while True:
            if self.blocked or random.randrange(4) != 0:
                self.heading = random.randrange(3)
                self.forward = random.choice((-1, 1))
            new_pos = self.advance()
            if self.is_empty(new_pos):
                self.current_pos = new_pos
                self.push(self.current_pos)
                self.tries = IQ;
                self.blocked = False
            else:
                self.blocked = True
                self.tries += 1
            if self.tries >= IQ:
                self.age()
                self.tries = 0
                return False
