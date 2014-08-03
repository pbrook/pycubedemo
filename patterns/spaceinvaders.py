# Copyright (C) John Leach <john@johnleach.co.uk>
# Released under the terms of the GNU General Public License version 3

import cubehelper
import httpinput
import math
import random


class Actor(object):
    def __init__(self, game, *args):
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
    def init(self):
        self.set_colour((0, 99, 0))
        self.centre_x()
        self.centre_y()
        self.z = 0

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

    def __init__(self, cube):
        self.cube = cube
        self.level = 10
        self.player = Player(self)
        self.invaders = [Invader(self)]
        self.landed = []
        self.bullets = []
        self.score = 0

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
        if self.arg is None:
            raise StopIteration
        port = int(self.arg)
        self.double_buffer = True
        self.game = Game(self.cube)
        buttons = [['forward'], ['left', 'fire#background-color: #ffcccc', 'right'],['back']]
        httpinput.StartHTTP(port, "LED Invaders", buttons, self.game.handle_action)
        return 0.1

    def tick(self):
        self.game.tick()
