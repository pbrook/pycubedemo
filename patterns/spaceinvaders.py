# Copyright (C) John Leach <john@johnleach.co.uk>
# Released under the terms of the GNU General Public License version 3

import cubehelper
import httpinput
import math
import random


class Actor(object):
    def __init__(self, game):
        self.game = game
        self.cube = self.game.cube
        self.set_position()
        self.set_colour()
        self.init()

    def set_colour(self, c=None):
        if c is None:
            c = cubehelper.random_color()
        self.colour = c

    def set_position(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

    def move_x(self, delta):
        self.x += delta
        if self.x < 0:
            self.x = 0
        if self.x > self.cube.size - 1:
            self.x = self.cube.size - 1

    def move_y(self, delta):
        self.y += delta
        if self.y < 0:
            self.y = 0
        if self.y > self.cube.size - 1:
            self.y = self.cube.size - 1

    def move_z(self, delta):
        self.z += delta
        if self.z < 0:
            self.z = 0
        if self.z > self.cube.size - 1:
            self.z = self.cube.size - 1

    def centre_x(self):
        self.x = self.cube.size / 2

    def centre_y(self):
        self.y = self.cube.size / 2

    def centre_z(self):
        self.z = self.cube.size / 2

    def coords(self):
        return (self.x, self.y, self.z)

    def draw(self):
        self.cube.set_pixel(self.coords(), self.colour)

    def collides_with(self, other):
        return self.coords() == other.coords()

    def init(self):
        pass

    def tick(self):
        pass


class Player(Actor):
    def __init__(self, game, ai):
        Actor.__init__(self, game)
        self.ai = ai

    def init(self):
        self.set_colour((0, 99, 0))
        self.centre_x()
        self.centre_y()
        self.z = 0
        self.ai_tick = 0
        self.target = None
        self.ignore = []

    def move_forward(self):
        self.move_y(1)

    def move_back(self):
        self.move_y(-1)

    def move_left(self):
        self.move_x(-1)

    def move_right(self):
        self.move_x(1)

    def fire(self):
        if len(self.game.bullets) < 3:
            bullet = Bullet(self.game)
            self.game.bullets.append(bullet)

    def tick(self):
        if not self.ai:
            return
        self.ai_tick += 1
        if self.ai_tick >= 4:
            return
        self.ai_tick = 0
        target = self.target
        if len(self.game.bullets) == 0:
            self.ignore = []
        while len(self.ignore) > 0 and self.ignore[0].state is not 'alive':
            self.ignore.pop(0)
        if (target is None) or (target.state is not 'alive'):
            target = None
            for invader in self.game.invaders:
                if invader in self.ignore:
                    continue
                if invader.state is not 'alive':
                    continue
                dist = abs(self.x - invader.x) + abs(self.y - invader.y)
                if target is None:
                    target = invader
                    target_dist = dist
                    continue
                if invader.z < target.z or (invader.z == target.z and dist < target_dist):
                    target = invader
                    target_dist = dist
            self.target = target

        if target is not None:
            if target.x > self.x:
                self.move_right()
            elif target.x < self.x:
                self.move_left()
            elif target.y > self.y:
                self.move_forward()
            elif target.y < self.y:
                self.move_back()
            else:
                self.fire();
                self.ignore.append(target)
                self.target = None


class Bullet(Actor):
    def init(self):
        self.set_colour((255, 255, 255))
        self.z = 0
        self.x = self.game.player.x
        self.y = self.game.player.y

        self.ticker = 0
        self.alive = True

    def tick(self):
        self.ticker += 1

        for invader in self.game.invaders:
            if self.collides_with(invader):
                invader.kill()
                self.game.bullets.remove(self)
                return
            if self.z >= self.cube.size-1:
                self.game.bullets.remove(self)
                return

        if self.ticker % 2 == 1:
            self.move_z(1)
            self.alive = self.z < self.cube.size-1


class Invader(Actor):
    def init(self):
        self.set_colour((255, 00, 00))
        self.x = random.randint(0, self.cube.size-1)
        self.y = random.randint(0, self.cube.size-1)
        self.z = self.cube.size-1
        self.speed = 20
        self.ticker = 0
        self.state = 'alive'
        self.opacity = 1.0

    def kill(self):
        self.game.score += 1
        self.state = 'dying'
        self.opacity = 0.5
        self.game.invaders.append(Invader(self.game))

    def tick(self):
        self.ticker += 1
        if self.state is 'alive':
            if self.ticker % self.speed == self.speed-1:
                self.move_z(-1)
            if self.z == 0:
                self.state = 'landed'
                self.opacity = 0.50
                self.game.score = max(0, self.game.score - 1)
                self.game.invaders.remove(self)
                self.game.landed.append(self)
                self.game.invaders.append(Invader(self.game))

        elif self.state is 'dying':
            self.opacity -= 0.1
            if self.opacity <= 0.0:
                self.opacity = 0
                self.state = 'dead'
        elif self.state is 'dead':
            self.game.invaders.remove(self)
        elif self.state is 'landed':
            self.opacity = 0.01 + (math.sin(self.ticker / 5.0) + 1.0) * (0.10 / 2.0)

    def draw(self):
        c = cubehelper.mix_color((0, 0, 0), self.colour, self.opacity)
        self.cube.set_pixel(self.coords(), c)

    def collides_with(self, other):
        return (self.state is 'alive' or self.state is 'landed') and \
            self.coords() == other.coords()


class Game(object):

    def __init__(self, cube, ai):
        self.cube = cube
        self.level = 10
        self.player = Player(self, ai)
        self.invaders = [Invader(self)]
        self.landed = []
        self.bullets = []
        if ai:
            self.score = 4
        else:
            self.score = 1

    def handle_action(self, action):
        if 'forward' in action:
            self.player.move_forward()
        elif 'back' in action:
            self.player.move_back()
        elif 'left' in action:
            self.player.move_left()
        elif 'right' in action:
            self.player.move_right()
        elif 'fire' in action:
            self.player.fire()
        else:
            raise ValueError

    def tick(self):
        self.cube.clear()
        self.player.tick()
        self.player.draw()
        for invader in self.invaders:
            invader.tick()
            invader.draw()
        for invader in self.landed:
            invader.tick()
            invader.draw()
        for bullet in self.bullets:
            bullet.tick()
            bullet.draw()

        for i in range(1, 10):
            if self.score >= i * 3 and len(self.invaders) <  i:
                self.invaders.append(Invader(self))


class Pattern(object):
    def init(self):
        self.double_buffer = True
        self.game = Game(self.cube, self.arg is None)
        buttons = [['forward'], ['left', 'fire#background-color: #ffcccc', 'right'],['back']]
        if self.arg is not None:
            port = int(self.arg)
            self.server = httpinput.StartHTTP(port, "LED Invaders", buttons, self.game.handle_action)
        return 0.1

    def tick(self):
        self.game.tick()
