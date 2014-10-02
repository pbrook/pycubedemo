from __future__ import with_statement
import cubehelper
import websocket
import json
import thread
import time
import copy
import numpy
import random
import pygame
import itertools
from threading import Lock
from collections import defaultdict

class Pattern(object):
    def init(self):
        self.double_buffer = True

        if self.arg is None:
            print("Error: pass the address of the DotField server websocket in the format host:port")
            time.sleep(1)
            raise StopIteration

        self.MAX_PIXEL_COLOR = [255, 255, 255]

        # Should white fading particles be shown at collision points?
        self.COLLISION_PARTICLES_ENABLED = True

        pygame.init()
        pygame.mixer.init()
        pygame.mixer.set_num_channels(24)

        # self.sample_plays = 0.0 # number of sample plays available
        self.sounds = [pygame.mixer.Sound('patterns/dotfield-data/Glock 32.%02d.wav' % f) for f in range(1, 28)]

        self.ps = ParticleSystem(self.cube.size)
        self.ps.set_collision_callback(self.particle_collision_handler)

        self.pixels_lock = Lock()
        self.pixels_to_set = []
        self.nyans_to_create = []

        self.colors = [] # set when the welcome message is received

        self.ews = EventedWebsocket("ws://%s/" % self.arg)
        self.ews.attach_handler('open', self.on_open)
        self.ews.attach_handler('welcome', self.on_welcome)
        self.ews.attach_handler('activate', self.on_activate)
        self.ews.attach_handler('nyan', self.on_nyan)
        self.ews.connect()

        self.collision_coords = []

        return 1.0/15

    def tick(self):
        self.ps.tick()

        # print ' %g' % self.sample_plays

        # if self.sample_plays < 3.0:
            # self.sample_plays += 0.1

        with self.pixels_lock:
            for ((x, y), face, startColor, endColor) in self.pixels_to_set:
                self.ps.add_new_dot_trail(
                        coord_xy=(x, y),
                        originating_face=face,
                        start_color=startColor,
                        end_color=endColor)

            for ((x, y), face) in self.nyans_to_create:
                self.ps.add_nyan_trail(
                    coord_xy=(x, y),
                    originating_face=face)

            self.pixels_to_set = []
            self.nyans_to_create = []

        rendered = self.ps.render()

        for y in xrange(self.cube.size):
            for x in xrange(self.cube.size):
                for z in xrange(self.cube.size):
                    self.cube.set_pixel((x, y, z), cubehelper.color_to_float(rendered[x][y][z]))

        for c in self.collision_coords:
            self.cube.set_pixel(c, 0xFFFFFF)
        self.collision_coords = []

    def particle_collision_handler(self, coordinates):
        """Handle a particle collision. coordinate is the x, y, z of the cell where the particles collided"""
        if self.COLLISION_PARTICLES_ENABLED:
            self.ps.add_collision_particle(coordinates)

        # if self.sample_plays < 0:
            # return

        sound = random.choice(self.sounds)
        sound.set_volume(random.uniform(0.3, 0.7))
        sound.play()
        # self.sample_plays -= 1.0

    def on_open(self):
        print("Connected to DotField server")
        self.ews.emit("hello")

    def on_welcome(self, data):
        if (data["app"] != "DotField"):
            print("Error: this isn't a DotField server! We're gonna do jack all about it though because we're lazy")
        else:
            self.colors = data["colors"]
            print("Successfully handshaken with server")

    def on_activate(self, data):
        with self.pixels_lock:
            # self.sound.play()
            startColor = self.colors[data["startColorIndex"]]
            endColor = self.colors[data["endColorIndex"]]
            translated_coords = self.translate_coords(data["coords"]["x"], data["coords"]["y"])
            self.pixels_to_set.append((translated_coords, data["face"], startColor, endColor))

    def on_nyan(self, data):
        with self.pixels_lock:
            translated_coords = self.translate_coords(data["coords"]["x"], data["coords"]["y"])
            self.nyans_to_create.append((translated_coords, data["face"]))

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
        self.framebuffer = numpy.zeros([cube_size, cube_size, cube_size, 3], dtype=int)

        self.particles = numpy.empty([cube_size, cube_size, cube_size], dtype=object)
        self.oob_particles = []

        # rainbow colours
        self.nyan_colors = [
            0xFF0000,
            0xFF6200,
            0xFFB700,
            0xEEFF00,
            0x80FF00,
            0x00FF0D,
            0x00FFE6,
            0x009DFF,
            0x0015FF,
            0x9500FF,
            0xE100FF
        ]

        self.clear_particles()

        # Unit vectors for particle movement AWAY from the named face of the cube
        self.directions = {
            'front': numpy.array([0, 1, 0]),
            'left': numpy.array([1, 0, 0]),
            'right': numpy.array([-1, 0, 0]),
            'back': numpy.array([0, -1, 0]),
            'top': numpy.array([0, 0, -1]),
            'bottom': numpy.array([0, 0, 1])
        }

    def tick(self):
        # Update each particle and move it into its new location
        ticked_particles = []
        for particle in self.get_particles():
            particle.tick()
            if not particle.dead:
                ticked_particles.append(particle)

        self.clear_particles()
        for particle in ticked_particles:
            self.store_particle(particle)

        # get rid of dead particles and check for collisions
        for x in xrange(self.cube_size):
            for y in xrange(self.cube_size):
                for z in xrange(self.cube_size):
                    current_bucket = self.particles[x][y][z]

                    if self.collision_callback and len(current_bucket) > 1:
                        # a collision may have happened. We only define a collision as between one or more
                        # trail heads and another particle, so check

                        if any((p.is_solid and p.is_head) for p in current_bucket):
                            # check every pair of particles to see if they collide (based on conditions)
                            for p1, p2 in itertools.combinations(current_bucket, 2):
                                if p1.collides_with(p2):
                                    self.collision_callback((x, y, z))

    def set_collision_callback(self, callback):
        self.collision_callback = callback

    def render(self):
        self.framebuffer = numpy.zeros([self.cube_size, self.cube_size, self.cube_size, 3], dtype=float)

        # draw the particles onto the framebuffer
        for particle in self.get_particles():
            particle.draw(self.framebuffer)

        return self.framebuffer

    def add_collision_particle(self, coord):
        particle = FadeParticle(self.cube_size)
        particle.init(coord, (1.0, 1.0, 1.0), 3, 0.05)
        self.store_particle(particle)

    def add_nyan_trail(self, coord_xy, originating_face):
        x, y = coord_xy
        coord = numpy.array(self.translate_to_3d(x, y, originating_face))

        inverse_direction = self.directions[originating_face] * -1

        for idx, col in enumerate(self.nyan_colors):
            particle = DotParticle(self.cube_size)
            particle.init(coord + inverse_direction*(idx+1), self.directions[originating_face], cubehelper.color_to_float(col), False)
            self.store_particle(particle)

    def add_new_dot_trail(self, coord_xy, originating_face, start_color, end_color):
        # translate the xy coordinate on the originating face to a cube 3D coordinate
        x, y = coord_xy
        coord = numpy.array(self.translate_to_3d(x, y, originating_face))

        end_color = cubehelper.color_to_float(end_color)

        # create some particles: one is the head of the trail, and the rest trailing behind.
        # for the trailing particles, transform the coordinate so the coords are behind the head
        inverse_direction = self.directions[originating_face] * -1

        # head particle
        particle_head = DotParticle(self.cube_size)
        particle_head.init(coord, self.directions[originating_face], cubehelper.color_to_float(start_color), True)
        self.store_particle(particle_head)

        # trail part 1
        particle_trail1 = DotParticle(self.cube_size)
        color = numpy.array(cubehelper.mix_color(start_color, end_color, 0.25)) * 0.7
        particle_trail1.init(coord + inverse_direction, self.directions[originating_face], color, False)
        self.store_particle(particle_trail1)

        # trail part 2
        particle_trail2 = DotParticle(self.cube_size)
        color = numpy.array(cubehelper.mix_color(start_color, end_color, 0.5)) * 0.5
        particle_trail2.init(coord + inverse_direction*2, self.directions[originating_face], color, False)
        self.store_particle(particle_trail2)

        # trail part 3
        particle_trail3 = DotParticle(self.cube_size)
        color = numpy.array(cubehelper.mix_color(start_color, end_color, 0.75)) * 0.3
        particle_trail3.init(coord + inverse_direction*3, self.directions[originating_face], color, False)
        self.store_particle(particle_trail3)

        # trail part 4
        particle_trail4 = DotParticle(self.cube_size)
        particle_trail4.init(coord + inverse_direction*4, self.directions[originating_face], numpy.array(end_color) * 0.1, False)
        self.store_particle(particle_trail4)

    def clear_particles(self):
        for x in xrange(self.cube_size):
            for y in xrange(self.cube_size):
                for z in xrange(self.cube_size):
                    self.particles[x][y][z] = []

        self.oob_particles[:] = [] # out-of-bounds particles (particles outside the cube)

    def get_particles(self):
        """Generator to iterate over all stored particles"""
        for x in xrange(self.cube_size):
            for y in xrange(self.cube_size):
                for z in xrange(self.cube_size):
                    for p in self.particles[x][y][z]:
                        yield p

        for particle in self.oob_particles:
            yield particle

    def store_particle(self, particle):
        """Insert the specified particle into a bucket corresponding to its location"""
        if particle.is_out_of_bounds():
            self.oob_particles.append(particle)
            return

        x, y, z = particle.location
        self.particles[x][y][z].append(particle)

    def dot_wall_collide(self, coordinate):
        print "Wall collision"

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
    """A solid particle that moves in a direction with constant velocity. Can optionally call a callback when colliding with a wall.
    Can optionally be a "head" particle, which can collide with other "head" particles. """

    MAX_PIXEL_COLOR = numpy.array([1.0, 1.0, 1.0])

    def __init__(self, cube_size):
        self.cube_size = cube_size
        self.is_solid = True # this particle CAN be involved in collisions

    def init(self, location, velocity, color, is_head):
        self.location = numpy.array(location)
        self.velocity = numpy.array(velocity)
        self.color = numpy.array(color) # array RGB float colours (0-1)
        self.is_head = is_head # is this particle the head of the trail?
        self.dead = False # set to true when the particle goes outside the bounds of the cube
        self.immune = self.is_out_of_bounds() # immune from dying. Used when spawning a particle outside the bounds of the cube
        self.wall_collision_callback = None

    def set_wall_collision_callback(self, callback):
        """This callback gets called when a particle hits the edge of the cube"""
        self.wall_collision_callback = callback

    def collides_with(self, other_particle):
        """Does the current particle collide with the other particle? This assumes you have ALREADY checked they're in the same location"""
        return other_particle.is_solid and self.is_head and other_particle.is_head and not numpy.array_equal(self.velocity, other_particle.velocity)

    def tick(self):
        old_location = numpy.copy(self.location)
        self.location += self.velocity

        oob = self.is_out_of_bounds()
        if oob and not self.immune:
            self.dead = True
        elif not oob:
            self.immune = False

        # Check to see if the particle has collided with the cube wall.
        # We can test for this by checking if any of the coordinate components are now on the cube wall, but weren't before.
        if self.wall_collision_callback:
            if ((self.location[0] != old_location[0] and (self.location[0] == 0 or self.location[0] == self.cube_size-1)) or
                    (self.location[1] != old_location[1] and (self.location[1] == 0 or self.location[1] == self.cube_size-1)) or
                    (self.location[2] != old_location[2] and (self.location[2] == 0 or self.location[2] == self.cube_size-1))):
                self.wall_collision_callback(self.location)

    def draw(self, framebuffer):
        """Draw this particle onto the passed-in framebuffer"""
        if not self.is_out_of_bounds():
            x, y, z = self.location
            framebuffer[x][y][z] = numpy.minimum(numpy.add(framebuffer[x][y][z], self.color), DotParticle.MAX_PIXEL_COLOR)

    def is_out_of_bounds(self):
        for l in self.location:
            if l < 0 or l >= self.cube_size:
                return True
        
        return False

class FadeParticle(object):
    """A static particle that stays a specified colour for a number of ticks, then linearly fades out until it disappears.
    It's not a solid particle, so nothing can collide with it."""

    MAX_PIXEL_COLOR = numpy.array([1.0, 1.0, 1.0])

    def __init__(self, cube_size):
        self.cube_size = cube_size
        self.is_solid = False # this particle cannot be collided with

    def init(self, location, color, sustain_ticks, fade_rate):
        """Initialise the fading particle. Specify the static location, the colour, the number of ticks
        to stay bright before fading, and how much brightness should be lost per tick"""

        self.location = numpy.array(location)
        self.x, self.y, self.z = self.location
        self.color = numpy.array(color)
        self.sustain_ticks = sustain_ticks
        self.fade_rate = fade_rate # 0.0 to 1.0
        self.current_brightness = 1.0
        self.dead = False

    def tick(self):
        if self.sustain_ticks > 0:
            self.sustain_ticks -= 1
            return

        self.current_brightness -= self.fade_rate

        if self.current_brightness <= 0:
            self.dead = True

    def draw(self, framebuffer):
        color_to_draw = cubehelper.mix_color(0x000000, self.color, self.current_brightness)
        framebuffer[self.x][self.y][self.z] = numpy.minimum(numpy.add(framebuffer[self.x][self.y][self.z], color_to_draw), FadeParticle.MAX_PIXEL_COLOR)

    def collides_with(self, other_particle):
        return False # we cannot collide as we aren't solid

    def is_out_of_bounds(self):
        for l in self.location:
            if l < 0 or l >= self.cube_size:
                return True
        
        return False
