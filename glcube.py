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
    gl_FragColor = vec4(color, 1.0f);
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
        width = 640
        height = 480
        size = args.size
        self.size = size
        self.pixels = numpy.zeros((size, size, size, 3), 'f')
        pygame.init()
        video_flags = pgl.OPENGL | pgl.DOUBLEBUF
        pygame.display.set_mode((width, height), video_flags)
        self.shader_init()
        self.geometry_init()
        self.projection = m0_projection(width/float(height), 1.0, 100.0)
        glEnable(GL_DEPTH_TEST)

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
        xoff = (self.size / 2 - 0.5) * -spacing
        yoff = (self.size / 2 - 0.5) * -spacing
        zoff = (self.size / 2 + 1) * spacing
        eye = numpy.array([[1.0, 0.0, 0.0, xoff],
                            [0.0, 0.0, 1.0, yoff],
                            [0.0, 1.0, 0.0, zoff],
                            [0.0, 0.0, 0.0, 1.0]
                           ], 'f')
        eye = numpy.dot(self.projection, eye)
        for pos in all_pixels():
            (x, y, z) = pos
            mpos[0, 3] = x * spacing
            mpos[1, 3] = y * spacing
            mpos[2, 3] = z * spacing
            m = numpy.dot(eye, mpos)

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
