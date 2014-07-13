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
void main()
{
    gl_Position = proj * vec4(position, 1.0);
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

    def render(self, attr):
        self.vec_vbo.bind()
        self.ind_vbo.bind()
        glVertexAttribPointer(attr, 3, GL_FLOAT, GL_FALSE, 12, self.vec_vbo)
        glDrawElements(GL_TRIANGLES, self.ind_count, GL_UNSIGNED_SHORT, self.ind_vbo)

def m0_projection(aspect, n, f):
    return numpy.array([[1.0, 0.0, 0.0, 0.0],
                        [0.0, aspect, 0.0, 0.0],
                        [0.0, 0.0, (f+n)/(f-n), -2.0*f*n/(f-n)],
                        [0.0, 0.0, 1.0, 0.0]], 'f')

class Cube(object):
    def __init__(self, args):
        self.color = True
        width = 640
        height = 480
        size = args.size
        self.size = size
        self.pixels = numpy.zeros((size, size, size, 3), 'f')
        pygame.init()
        video_flags = pgl.OPENGL | pgl.DOUBLEBUF
        pygame.display.set_mode((width, height), video_flags)
        pygame.key.set_repeat(30, 30)
        self.shader_init()
        self.geometry_init()
        self.projection = m0_projection(width/float(height), 1.0, 100.0)
        glEnable(GL_DEPTH_TEST)
        self.keyboard_speed = math.pi / 32
        self.mouse_speed = math.pi / 400
        self.alpha = 0
        self.beta = 0
        self.dragging = False
        self.update_rotation()

    def shader_init(self):
        vertex = shaders.compileShader(vertex_code, GL_VERTEX_SHADER)
        fragment = shaders.compileShader(fragment_code, GL_FRAGMENT_SHADER)
        program = shaders.compileProgram(vertex, fragment)
        self.shader = program
        self.attr_position = glGetAttribLocation(program, "position")
        self.param_color = glGetUniformLocation(program, "color")
        self.param_proj = glGetUniformLocation(program, "proj")

    def geometry_init(self):
        self.pixel_model = Model("pixel.off")

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

    def update_rotation(self):
        self.alpha = max(-math.pi/2, min(self.alpha, math.pi/2))
        ca = math.cos(self.alpha)
        sa = math.sin(self.alpha)
        cb = math.cos(self.beta)
        sb = math.sin(self.beta)
        rot1 = numpy.array([[1.0, 0.0, 0.0, 0.0],
                            [0.0, ca,  sa,  0.0],
                            [0.0, -sa, ca,  0.0],
                            [0.0, 0.0, 0.0, 1.0]
                           ], 'f')
        rot2 = numpy.array([[cb,  sb,  0.0, 0.0],
                            [-sb, cb,  0.0, 0.0],
                            [0.0, 0.0, 1.0, 0.0],
                            [0.0, 0.0, 0.0, 1.0]
                           ], 'f')
        self.rot = numpy.dot(rot1, rot2)

    def render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(self.shader)
        glEnableVertexAttribArray(self.attr_position)

        mpos = numpy.identity(4, 'f')
        def all_pixels():
            for x in range(0, self.size):
                for y in range(0, self.size):
                    for z in range(0, self.size):
                        yield (x, y, z)
        spacing = 5.0
        xoff = 0
        yoff = 0
        zoff = (self.size  + 2) * spacing
        eye = numpy.array([[1.0, 0.0, 0.0, xoff],
                            [0.0, 0.0, 1.0, yoff],
                            [0.0, 1.0, 0.0, zoff],
                            [0.0, 0.0, 0.0, 1.0]
                           ], 'f')
        eye = numpy.dot(self.projection, eye)
        for pos in all_pixels():
            (x, y, z) = pos
            mpos[0, 3] = (x - self.size/2 + 0.5) * spacing
            mpos[1, 3] = (y - self.size/2 + 0.5) * spacing
            mpos[2, 3] = (z - self.size/2 + 0.5) * spacing
            m = numpy.dot(self.rot, mpos)
            m = numpy.dot(eye, m)
            glUniformMatrix4fv(self.param_proj, 1, GL_TRUE, m)
            glUniform3fv(self.param_color, 1, self.pixels[pos])
            self.pixel_model.render(self.attr_position)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pgl.QUIT:
                return True
            if event.type == pgl.KEYUP:
                if event.key == pgl.K_ESCAPE or event.key == ord('q'):
                    return True
                if event.key == pgl.K_SPACE:
                    raise StopIteration
                if event.key == ord('r'):
                        self.alpha = self.beta = 0
                        self.update_rotation()
            if event.type == pgl.MOUSEBUTTONDOWN:
                self.dragging = True
                pygame.mouse.get_rel()
            if event.type == pgl.MOUSEBUTTONUP:
                self.dragging = False
            if event.type == pgl.MOUSEMOTION and self.dragging:
                ms = self.mouse_speed
                delta = pygame.mouse.get_rel()
                self.beta -= delta[0] * ms 
                self.alpha -= delta[1] * ms
                self.update_rotation()
            if event.type == pgl.KEYDOWN:
                ks = self.keyboard_speed
                if event.key == ord('w') or event.key == pgl.K_UP:
                    self.alpha += ks
                if event.key == ord('s') or event.key == pgl.K_DOWN:
                    self.alpha -= ks
                if event.key == ord('a') or event.key == pgl.K_LEFT:
                    self.beta += ks
                if event.key == ord('d') or event.key == pgl.K_RIGHT:
                    self.beta -= ks
                self.update_rotation()
