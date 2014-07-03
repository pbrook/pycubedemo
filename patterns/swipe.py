# Swipe a plane of pixels accross the cube

class Pattern(object):
    def __init__(self, cube):
        self.cube = cube
        self.name = "swipe"

    def init(self):
        self.phase = 0
        self.offset = 0
        return 0.2
    def tick(self):
        p0 = self.phase
        p1 = (p0 + 1) % 3
        p2 = (p1 + 1) % 3
        pos = [0]*3
        off = [0]*3
        on = [0]*3
        on[p0] = 255
        for i in range(0, self.cube.size):
            if i == self.offset:
                color = on
            else:
                color = off
            pos[p0] = i
            for j in range(0, self.cube.size):
                pos[p1] = j
                for k in range(0, self.cube.size):
                    pos[p2] = k
                    self.cube.set_pixel(pos, color)
        self.offset += 1
        if self.offset == self.cube.size:
            self.offset = 0
            self.phase += 1
            if self.phase == 3:
                raise StopIteration;
