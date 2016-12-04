# OpenGL LED cube renderer
# Copyright (C) Paul Brook <paul@nowt.org>
# Released under the terms of the GNU General Public License version 3

from OpenGL.GL import *
from OpenGL.GL import shaders
from OpenGL.GLU import *
from OpenGL.arrays import vbo
import pygame
import pygame.locals as pgl
import numpy
import cubehelper
import math

vertex_code = """
attribute vec3 position;
uniform mat4 proj;
uniform mat4 rot;
uniform vec3 offset;
void main()
{
    gl_Position = proj * rot * vec4(position + offset, 1.0);
}
"""

fragment_code = """
uniform vec3 color;
void main()
{
    gl_FragColor = vec4(color, 1.0);
}
"""

class Model(object):
    def __init__(self, filename):
        f = open(filename, "rt")
        l = f.readline().strip()
        if l != 'OFF':
            raise Exception("Bad object file: '%s'" % filename)
        l = f.readline().strip()
        a = l.split()
        npoints = int(a[0])
        nfaces = int(a[1])
        f.readline()
        data = numpy.zeros((npoints, 3), 'f')
        for n in range(0, npoints):
            l = f.readline().strip()
            data[n] = [float(x) for x in l.split()]
        self.vec_vbo = vbo.VBO(data)
        data = numpy.zeros((nfaces, 3), numpy.uint16)
        for n in range(0, nfaces):
            l = f.readline().strip()
            a = [float(x) for x in l.split()]
            if a[0] != 3:
                raise Exception("Triangle with %d corners" % a[0])
            data[n] = a[1:4]
        self.ind_vbo = vbo.VBO(data, target=GL_ELEMENT_ARRAY_BUFFER)
        self.ind_count = nfaces * 3

    def bind(self, attr):
        self.vec_vbo.bind()
        self.ind_vbo.bind()
        glVertexAttribPointer(attr, 3, GL_FLOAT, GL_FALSE, 12, self.vec_vbo)

    def render(self):
        glDrawElements(GL_TRIANGLES, self.ind_count, GL_UNSIGNED_SHORT, self.ind_vbo)

def m0_projection(aspect, n, f):
    return numpy.array([[1.0, 0.0, 0.0, 0.0],
                        [0.0, aspect, 0.0, 0.0],
                        [0.0, 0.0, (f+n)/(f-n), -2.0*f*n/(f-n)],
                        [0.0, 0.0, 1.0, 0.0]], 'f')

class Cube(object):
    def __init__(self, args):
        self.color = True
        self.width = 640
        self.height = 480
        size = args.size
        self.size = size
        self.pixels = numpy.zeros((size, size, size, 3), 'f')
        pygame.init()
        pygame.key.set_repeat(20, 20)
        self.video_init()
        self.shader_init()
        self.geometry_init()
        glEnable(GL_DEPTH_TEST)
        self.keyboard_speed = math.pi / 32
        self.mouse_speed = math.pi / 400
        self.alpha = 0
        self.beta = 0
        self.dragging = False
        self.update_rotation()

    def video_init(self):
        (w, h) = (self.width, self.height)
        video_flags = pgl.OPENGL | pgl.DOUBLEBUF | pgl.RESIZABLE
        pygame.display.set_mode((w, h), video_flags)
        glViewport (0, 0, w, h)
        self.projection = m0_projection(w/float(h), 1.0, 100.0)
        pygame.display.set_caption(u"Cubulator\u2122".encode('utf8'))

    def shader_init(self):
        vertex = shaders.compileShader(vertex_code, GL_VERTEX_SHADER)
        fragment = shaders.compileShader(fragment_code, GL_FRAGMENT_SHADER)
        program = shaders.compileProgram(vertex, fragment)
        self.shader = program
        self.attr_position = glGetAttribLocation(program, "position")
        self.param_color = glGetUniformLocation(program, "color")
        self.param_proj = glGetUniformLocation(program, "proj")
        self.param_rot = glGetUniformLocation(program, "rot")
        self.param_offset = glGetUniformLocation(program, "offset")

    def geometry_init(self):
        self.pixel_model = Model("pixel.off")

    def update_rotation(self):
        self.alpha = max(-math.pi/2, min(self.alpha, math.pi/2))
        ca = math.cos(self.alpha)
        sa = math.sin(self.alpha)
        cb = math.cos(self.beta)
        sb = math.sin(self.beta)
        rot1 = numpy.array([[1.0, 0.0, 0.0, 0.0],
                            [0.0, ca, sa, 0.0],
                            [0.0, -sa, ca, 0.0],
                            [0.0, 0.0, 0.0, 1.0]
                        ], 'f')
        rot2 = numpy.array([[cb, sb, 0.0, 0.0],
                            [-sb, cb, 0.0, 0.0],
                            [0.0, 0.0, 1.0, 0.0],
                            [0.0, 0.0, 0.0, 1.0]
                        ], 'f')
        self.rot = numpy.dot(rot1, rot2)

    def set_pixel(self, xyz, rgb):
        rgb = cubehelper.color_to_float(rgb)
        self.pixels[tuple(xyz)] = rgb

    def clear(self):
        self.pixels.fill(0.0)

    def single_buffer(self):
        pass

    def swap(self):
        # We are effectively double buffered, so no need to do anything here
        pass

    def render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(self.shader)
        glEnableVertexAttribArray(self.attr_position)
        self.pixel_model.bind(self.attr_position)

        spacing = 5.0
        xoff = (self.size / 2 - 0.5) * -spacing
        yoff = (self.size / 2 - 0.5) * -spacing
        zoff = (self.size + 2) * spacing
        eye = numpy.array([[1.0, 0.0, 0.0, 0],
                            [0.0, 0.0, 1.0, 0],
                            [0.0, 1.0, 0.0, zoff],
                            [0.0, 0.0, 0.0, 1.0]
                           ], 'f')
        eye = numpy.dot(self.projection, eye)
        glUniformMatrix4fv(self.param_proj, 1, GL_TRUE, eye)
        glUniformMatrix4fv(self.param_rot, 1, GL_TRUE, self.rot)
        for x in range(0, self.size):
            for y in range(0, self.size):
                for z in range(0, self.size):
                    (r, g, b) = self.pixels[x, y, z]
                    glUniform3f(self.param_color, r, g, b)
                    glUniform3f(self.param_offset, 
                                (x - self.size/2 + 0.5) * spacing,
                                (y - self.size/2 + 0.5) * spacing,
                                (z - self.size/2 + 0.5) * spacing)
                    self.pixel_model.render()
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pgl.QUIT:
                raise KeyboardInterrupt
            if event.type == pgl.VIDEORESIZE:
                (self.width, self.height) = event.dict['size']
                self.video_init()
            if event.type == pgl.KEYUP:
                if event.key == pgl.K_ESCAPE or event.key == ord('q'):
                    raise KeyboardInterrupt
                if event.key == pgl.K_SPACE:
                    raise StopIteration
                if event.key == ord('r'):
                    self.alpha = self.beta = 0
                    self.update_rotation()
            if event.type == pgl.MOUSEBUTTONDOWN:
                self.dragging = True
                pygame.mouse.set_visible(False)
                pygame.event.set_grab(True)
                pygame.mouse.get_rel()
            if event.type == pgl.MOUSEBUTTONUP:
                self.dragging = False
                pygame.mouse.set_visible(True)
                pygame.event.set_grab(False)
            if event.type == pgl.MOUSEMOTION and self.dragging:
                ms = self.mouse_speed
                (dx, dy) = pygame.mouse.get_rel()
                self.beta -= dx * ms
                self.alpha -= dy * ms
                self.update_rotation()
            if event.type == pgl.KEYDOWN:
                ks = self.keyboard_speed
                if event.key == ord('w') or event.key == pgl.K_UP:
                    self.alpha += ks
                elif event.key == ord('s') or event.key == pgl.K_DOWN:
                    self.alpha -= ks
                elif event.key == ord('a') or event.key == pgl.K_LEFT:
                    self.beta += ks
                elif event.key == ord('d') or event.key == pgl.K_RIGHT:
                    self.beta -= ks
                else:
                    continue
                self.update_rotation()
