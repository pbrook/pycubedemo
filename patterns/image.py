# Fade the whole cube in and out a single color
# Copyright (C) Paul Brook <paul@nowt.org>
# Released under the terms of the GNU General Public License version 3

import cubehelper
import PIL.Image
import numpy

def load_frames(im):
    (w, h) = im.size
    if im.palette is not None:
        src = im.palette.palette
        palette = [0]*256
        for i in range(256):
            r = ord(src[i * 3])
            g = ord(src[i * 3 + 1])
            b = ord(src[i * 3 + 2])
            palette[i] = (r << 16) | (g << 8) | b
    else:
        palette = None
    try:
        while True:
            ar = numpy.zeros((w, h), 'i')
            for x in range(0, w):
                for y in range(0, h):
                    color = im.getpixel((x, y))
                    if palette is not None:
                        color = palette[color]
                    ar[x, y] = color
            yield ar
            im.seek(im.tell() + 1)
    except EOFError:
        raise StopIteration

class Pattern(object):
    def init(self):
        self.double_buffer = True
        if self.arg is None:
            raise StopIteration
        try:
            im = PIL.Image.open(self.arg)
            sz = self.cube.size
            if im.size != (sz * sz, sz):
                raise StopIteration
            self.frames = list(load_frames(im))
            self.current_frame = 0
            try:
                delay = im.info['duration'] / 100.0
                if delay < 0.1:
                    delay = 0.1
            except:
                delay = 0.1
        except Exception as e:
            print(e)
            raise StopIteration
        return delay


    def tick(self):
        sz = self.cube.size
        data = self.frames[self.current_frame]
        for y in range(0, sz):
            for z in range(0, sz):
                for x in range(0, sz):
                    color = int(data[x + y * sz, sz - (z + 1)])
                    self.cube.set_pixel((x, y, z), color)
        num_frames = len(self.frames)
        if num_frames == 1:
            return
        self.current_frame += 1
        if self.current_frame == num_frames:
            self.current_frame = 0
            raise StopIteration

