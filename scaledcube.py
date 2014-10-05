# Supersampled virtual cube with gamma correction
# Tom Hargreaves <hex@freezone.co.uk>
import numpy
import cubehelper

class Cube(object):
    def __init__(self, args):
        self.realcube = args.realcube
        self.color = self.realcube.color
        size = args.size
        self.realsize = size
        sc = args.scale
        self.scale = sc
        self.size = size*sc
        self.gamma = args.gamma
        self.pixels = numpy.zeros((size*sc, size*sc, size*sc, 3), 'f')

    def set_pixel(self, xyz, rgb):
        rgb = cubehelper.color_to_float(rgb)
        self.pixels[tuple(xyz)] = rgb

    def clear(self):
        self.pixels.fill(0.0)

    def single_buffer(self):
        pass

    def swap(self):
        pass

    def render(self):
        sc = self.scale
        gamma = self.gamma
        igamma = 1/self.gamma
        sc3 = sc * sc * sc
        for x in range(0, self.realsize):
            for y in range(0, self.realsize):
                for z in range(0, self.realsize):
                    (r, g, b) = (0, 0, 0)
                    for xx in range(0, sc):
                        for yy in range(0, sc):
                            for zz in range(0, sc):
                                (rr,gg,bb) = self.pixels[x*sc+xx, y*sc+yy, z*sc+zz]
                                r += rr**gamma
                                g += gg**gamma
                                b += bb**gamma
                        self.realcube.set_pixel((x,y,z), 
                                                ((r/sc3)**igamma,
                                                 (g/sc3)**igamma,
                                                 (b/sc3)**igamma))
        self.realcube.render()
