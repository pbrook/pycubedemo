from __future__ import with_statement
import cubehelper
import websocket
import json
import thread
import time
import copy
import numpy
import pygame
from threading import Lock
from collections import defaultdict

class Pattern(object):
    def init(self):
        self.double_buffer = True

        if self.arg is None:
            print("Error: pass the address of the GravityBlocks server websocket in the format host:port")
            time.sleep(1)
            raise StopIteration

        self.MAX_PIXEL_COLOR = [255, 255, 255]

        pygame.init()
        pygame.mixer.init()

        self.ps = ParticleSystem(self.cube.size)

        self.pixels_lock = Lock()
        self.pixels_to_set = []

        self.colors = [] # set when the welcome message is received

        self.ews = EventedWebsocket("ws://%s/" % self.arg)
        self.ews.attach_handler('open', self.on_open)
        self.ews.attach_handler('welcome', self.on_welcome)
        self.ews.attach_handler('activate', self.on_activate)
        self.ews.connect()

        return 1.0/15

    def tick(self):
        self.ps.tick()

        with self.pixels_lock:
            for ((x, y), face, color) in self.pixels_to_set:
                self.ps.add_new_dot_particle(
                        coord_xy=(x, y),
                        originating_face=face,
                        color=color)

            self.pixels_to_set = []

        rendered = self.ps.render()

        for y in xrange(self.cube.size):
            for x in xrange(self.cube.size):
                for z in xrange(self.cube.size):
                    self.cube.set_pixel((x, y, z), cubehelper.color_to_float(rendered[x][y][z]))

    def on_open(self):
        print("Connected to GravityBlocks server")
        self.ews.emit("hello")

    def on_welcome(self, data):
        if (data["app"] != "GravityBlocks"):
            print("Error: this isn't a GravityBlocks server! We're gonna do jack all about it though because we're lazy")
        else:
            self.colors = data["colors"]
            print("Successfully handshaken with server")

    def on_activate(self, data):
        with self.pixels_lock:
            color = self.colors[data["color"]]
            translated_coords = self.translate_coords(data["coords"]["x"], data["coords"]["y"])
            self.pixels_to_set.append((translated_coords, data["face"], color))

    def translate_coords(self, x, y):
        """ Translate finger-coordinates (i.e. top left is 0, 0, bottom left is 0, 7) to plane coords (i.e. top left
            is 0, 7, bottom left is 0, 0). Plane coords use x and y axes """
        return (x, self.cube.size - y - 1)

class EventedWebsocket(object):
    def __init__(self, url):
        self.event_handlers = defaultdict(list)
        self.connect_url = url

    def connect(self):
        self.ws = websocket.WebSocketApp(self.connect_url,
                            on_message = self.on_message,
                            on_error = self.on_error,
                            on_open = self.on_open,
                            on_close = self.on_close)
        thread.start_new_thread(self.ws.run_forever, ())

    def emit(self, event, data=None):
        if data == None:
            self.ws.send(event)
        else:
            self.ws.send(event + "|" + json.dumps(data))

    def attach_handler(self, event, callable):
        self.event_handlers[event].append(callable)

    def run_handlers(self, event, *args):
        for handler in self.event_handlers[event]:
            handler(*args)

    def on_message(self, ws, message):
        """
        Handle an incoming websocket message. Our protocol will either send a string on its
        own, in which case it's just an event, or it will be in the format
        eventname|{'optional': 'jsondata'} which is an event with a JSON data payload
        """

        self.run_handlers("message", message)

        parts = message.split("|", 1)
        if len(parts) == 1:
            self.run_handlers(parts[0])
        else:
            self.run_handlers(parts[0], json.loads(parts[1]))

    def on_error(self, ws, error):
        self.run_handlers("error", error)

    def on_open(self, ws):
        self.run_handlers("open")

    def on_close(self, ws):
        self.run_handlers("close")


class ParticleSystem(object):
    def __init__(self, cube_size):
        self.cube_size = cube_size
        self.particles = []
        self.framebuffer = numpy.zeros([cube_size, cube_size, cube_size, 3], dtype=int)

        self.sound = pygame.mixer.Sound('patterns/gravityblocks-data/harp-a.wav')

        # Unit vectors for particle movement AWAY from the named face of the cube
        self.directions = {
            'front': [0, 1, 0],
            'left': [1, 0, 0],
            'right': [-1, 0, 0],
            'back': [0, -1, 0],
            'top': [0, 0, -1],
            'bottom': [0, 0, 1]
        }

    def tick(self):
        for particle in self.particles:
            particle.tick()

        # get rid of dead particles
        self.particles[:] = [p for p in self.particles if p.dead == False]

    def render(self):
        # decay the framebuffer (make it slightly dimmer)
        for x in xrange(self.cube_size):
            for y in xrange(self.cube_size):
                for z in xrange(self.cube_size):
                    self.framebuffer[x][y][z][0] = max(self.framebuffer[x][y][z][0] - 70, 0) # ensure it can't be less than 0
                    self.framebuffer[x][y][z][1] = max(self.framebuffer[x][y][z][1] - 70, 0)
                    self.framebuffer[x][y][z][2] = max(self.framebuffer[x][y][z][2] - 70, 0)

        # draw the new locations of the particles
        for particle in self.particles:
            particle.draw(self.framebuffer)

        return self.framebuffer

    def add_new_dot_particle(self, coord_xy, originating_face, color):
        new_particle = DotParticle(self.cube_size)

        # translate the xy coordinate on the originating face to a cube 3D coordinate
        x, y = coord_xy
        coord = self.translate_to_3d(x, y, originating_face)

        new_particle.init(coord, self.directions[originating_face], color)
        new_particle.set_wall_collision_callback(self.dot_wall_collide)
        self.particles.append(new_particle)

    def dot_wall_collide(self, coordinate):
        print "Wall collision"
        self.sound.play()

    def translate_to_3d(self, x, y, face):
        """Translate a coordinate specified in 2D on a cube face to 3D cube coordinates"""
        cs = self.cube_size-1

        if face == 'front':
            return [x, 0, y]
        elif face == 'left':
            return [0, cs-x, y]
        elif face == 'right':
            return [cs, x, y]
        elif face == 'back':
            return [cs-x, cs, y]
        elif face == 'bottom':
            return [x, y, 0]
        elif face == 'top':
            return [x, y, cs]


class DotParticle(object):
    MAX_PIXEL_COLOR = numpy.array([255, 255, 255])

    def __init__(self, cube_size):
        self.cube_size = cube_size

    def init(self, location, velocity, color):
        self.location = numpy.array(location)
        self.velocity = numpy.array(velocity)
        self.color = numpy.array(color)
        self.dead = False # set to true when the particle goes outside the bounds of the cube
        self.immune = self._is_out_of_bounds() # immune from dying. Used when spawning a particle outside the bounds of the cube
        self.wall_collision_callback = None

    def set_wall_collision_callback(self, callback):
        """This callback gets called when a particle hits the edge of the cube"""
        self.wall_collision_callback = callback

    def tick(self):
        old_location = numpy.copy(self.location)
        self.location += self.velocity

        oob = self._is_out_of_bounds()
        if oob and not self.immune:
            self.dead = True
        elif not oob:
            self.immune = False

        # Check to see if the particle has collided with the cube wall.
        # We can test for this by checking if any of the coordinate components are now on the cube wall, but weren't before.
        if ((self.location[0] != old_location[0] and (self.location[0] == 0 or self.location[0] == self.cube_size-1)) or
            (self.location[1] != old_location[1] and (self.location[1] == 0 or self.location[1] == self.cube_size-1)) or
            (self.location[2] != old_location[2] and (self.location[2] == 0 or self.location[2] == self.cube_size-1))):
            if self.wall_collision_callback:
                self.wall_collision_callback(self.location)

    def draw(self, framebuffer):
        """Draw this particle onto the passed-in framebuffer"""
        x, y, z = self.location
        framebuffer[x][y][z] = numpy.minimum(numpy.add(framebuffer[x][y][z], self.color), DotParticle.MAX_PIXEL_COLOR)

    def _is_out_of_bounds(self):
        return bool([l for l in self.location if l >= self.cube_size or l < 0])
