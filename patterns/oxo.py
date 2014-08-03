# Noughts and Crosses
# Copyright (C) Paul Brook <paul@nowt.org>
# Released under the terms of the GNU General Public License version 3

import random
import cubehelper
import math
import numpy
import itertools
import httpinput

DT = 1.0/25

WIN_DELAY = 2.0
TURN_DELAY = 0.3

WHITE = 0xffffff
RED = 0xff0000
BLUE = 0x0000ff

def diagonals():
    for x in range(0, 4):
        for y in range(0, 4):
            yield [(x, y, i) for i in range(0,4)]
            yield [(x, i, y) for i in range(0,4)]
            yield [(i, x, y) for i in range(0,4)]
        yield [(x, i, i) for i in range(0,4)]
        yield [(x, i, 3-i) for i in range(0,4)]
        yield [(i, x, i) for i in range(0,4)]
        yield [(i, x, 3-i) for i in range(0,4)]
        yield [(i, i, x) for i in range(0,4)]
        yield [(i, 3-i, x) for i in range(0,4)]
    yield [(i, i, i) for i in range(0,4)]
    yield [(i, i, 3-i) for i in range(0,4)]
    yield [(i, 3-i, i) for i in range(0,4)]
    yield [(i, 3-i, 3-i) for i in range(0,4)]

class Pattern(object):
    def __init__(self):
        self.server = None

    def init(self):
        self.grid = numpy.zeros((4,4,4), 'i')
        self.double_buffer = True
        self.cursor = [0, 0, 0]
        self.ccount = 0.0
        self.cdelta = 5.0
        self.coffset_iter = itertools.cycle([(0,0), (0, 1), (1, 1), (1, 0)])
        self.coffset = next(self.coffset_iter)
        self.cnext = next(self.coffset_iter)
        self.current_player = 0
        self.won_line = None
        self.winner = None
        if self.server is None and self.arg is not None:
            port = int(self.arg)
            buttons = [['up', 'out'], ['down', 'in'], ['left', 'right'], ['place']]
            self.server = httpinput.StartHTTP(port, 'OXO', buttons, self.action)
        self.ai_tick = TURN_DELAY
        return DT

    def check_won(self):
        val = self.current_player + 1
        for l in diagonals():
            won = True
            for (x, y, z) in l:
                if self.grid[x, y, z] != val:
                    won = False
                    break
            if won:
                self.won_line = l;
                self.winner = self.current_player
        if self.winner is None:
            if numpy.all(self.grid):
                self.winner = -1
        if self.winner is not None:
            self.ai_tick = WIN_DELAY

    def ai_find_pos(self):
        ai_score = {}
        def change_score(pos, delta):
            if pos in ai_score:
                ai_score[pos] += delta
            else:
                ai_score[pos] = delta
        my_val = self.current_player + 1
        other_3 = None
        for l in diagonals():
            free = set()
            mine = set()
            other = set()
            for pos in l:
                val = self.grid[pos]
                if val == 0:
                    free.add(pos)
                elif val == my_val:
                    mine.add(pos)
                else:
                    other.add(pos)
            if len(free) == 0:
                continue
            if len(mine) == 3:
                return free.pop()
            if len(other) == 3:
                other_3 = free.pop()
            for pos in free:
                if (len(other) > 0) and (len(mine) > 0):
                    change_score(pos, -1)
                elif (len(mine) >= 2) or (len(other) >= 2):
                    # Disabling this makes the AI dumb
                    change_score(pos, 1)
                else:
                    change_score(pos, 0)
        if other_3 is not None:
            return other_3
        best = set()
        best_score = -1000
        for pos in ai_score:
            if ai_score[pos] > best_score:
                best = set([pos])
                best_score = ai_score[pos]
            elif ai_score[pos] == best_score:
                best.add(pos)
        return random.choice(list(best))

    def do_ai(self):
        pos = self.ai_find_pos()
        self.cursor = list(pos)
        self.set_block()

    def move_cursor(self, axis, val):
        x = self.cursor[axis] + val;
        if (x >= 0) and (x < 4):
            self.cursor[axis] = x;

    def set_block(self):
        pos = tuple(self.cursor)
        if self.grid[pos] != 0:
            return
        self.grid[pos] = self.current_player + 1
        self.check_won()
        if self.winner is None:
            self.current_player = 1 - self.current_player

    def action(self, action):
        al = action.split('/')
        if len(al) != 3:
            return
        player = int(al[1]) - 1
        if (player < 0) or (player > 2):
            raise ValueError
        if player != self.current_player:
            return
        if self.winner is not None:
            return
        cmd = al[2]
        if cmd == 'up':
            self.move_cursor(2, 1)
        elif cmd == 'down':
            self.move_cursor(2, -1)
        elif cmd == 'left':
            self.move_cursor(0, -1)
        elif cmd == 'right':
            self.move_cursor(0, 1)
        elif cmd == 'in':
            self.move_cursor(1, -1)
        elif cmd == 'out':
            self.move_cursor(1, 1)
        elif cmd == 'place':
            self.set_block()
        else:
            raise ValueError

    def box(self, x, y, z, color):
        x *= 2
        y *= 2
        z *= 2
        for i in range(x, x + 2):
            for j in range(y, y + 2):
                for k in range(z, z + 2):
                    self.cube.set_pixel((i, j, k), color)

    def tick(self):
        def draw_cursor(pos):
            (x, y, z) = pos
            base = color_lut[self.grid[x, y, z]]
            x *= 2
            y *= 2
            z *= 2
            color = cubehelper.mix_color(base, WHITE, 1.0 - self.ccount)
            (i, j) = self.coffset
            self.cube.set_pixel((x+i,y+j,z), color)
            self.cube.set_pixel((x+1-i,y+1-j,z+1), color)
            color = cubehelper.mix_color(base, WHITE, self.ccount)
            (i, j) = self.cnext
            self.cube.set_pixel((x+i,y+j,z), color)
            self.cube.set_pixel((x+1-i,y+1-j,z+1), color)

        color_lut = [0, RED, BLUE]
        dim = 2 - self.current_player
        color_lut[dim] = cubehelper.mix_color(0, color_lut[dim], 0.70)
        for y in range(0, 4):
            for z in range(0, 4):
                for x in range(0, 4):
                    color = color_lut[self.grid[x, y, z]]
                    self.box(x, y, z, color)
        if self.winner is None:
            draw_cursor(self.cursor)
        if self.won_line is not None:
            for pos in self.won_line:
                draw_cursor(pos)
        self.ccount += self.cdelta * DT
        if self.ccount > 1.0:
            self.ccount -= 1.0
            self.coffset = self.cnext
            self.cnext = next(self.coffset_iter)
        if (self.current_player == 1) or (self.server is None) or (self.winner is not None):
            self.ai_tick -= DT
        if self.ai_tick < 0:
            if self.winner is not None:
                raise StopIteration
            self.ai_tick = TURN_DELAY
            self.do_ai()
