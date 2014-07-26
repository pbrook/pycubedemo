import random
import numbers
import math

def line(p0, p1):
    d = [abs(p0[i] - p1[i]) for i in range(0, 3)]
    if d[0] > d[1]:
        a0 = 0
    else:
        a0 = 1
    a1 = 1 - a0
    if d[2] > d[a0]:
        a2 = a0
        a0 = 2
    else:
        a2 = 2
    if p0[a0] > p1[a0]:
        (p0, p1) = (p1, p0)
    dx = float(p1[a0] - p0[a0])
    #print((a0, a1, a2), dx)
    if dx < 1.0:
        yield tuple(int(v) for v in p0)
        return
    dy = float(p1[a1] - p0[a1]) / dx
    dz = float(p1[a2] - p0[a2]) / dx
    #print([dx, dy, dz])
    y = float(p0[a1]) + 0.5
    z = float(p0[a2]) + 0.5
    pos = [0.0]*3
    for x in range(int(p0[a0]), int(p1[a0]) + 1):
        pos[a0] = x
        pos[a1] = int(y)
        pos[a2] = int(z)
        yield tuple(pos)
        y += dy
        z += dz

def random_color():
    r = 0
    g = 0
    b = 0
    while r == 0 and g == 0 and b == 0:
        r = random.randrange(2)
        g = random.randrange(2)
        b = random.randrange(2)
    return (float(r), float(g), float(b))

def pos_modf(val):
    val = math.modf(val)[0]
    if val < 0:
        return val + 1.0
    return val

def color_plasma(val):
    val = pos_modf(val) * 3.0
    if val < 1.0:
        r = val
        g = 1.0 - r
        b = 0.0
    elif val < 2.0:
        b = val - 1.0
        r = 1.0 - b
        g = 0.0
    else:
        g = val - 2.0
        b = 1.0 - g
        r = 0.0
    return (r, g, b)

def mono_plasma(val):
    val = pos_modf(val) * 2.0
    if val > 1.0:
        val = 2.0 - val
    return (val, val, val)

def mix_color(color0, color1, level):
    f0 = color_to_float(color0)
    f1 = color_to_float(color1)
    return tuple([f1[n] * level + f0[n] * (1.0 - level) for n in range(0, 3)])

def color_to_hex(color):
    if isinstance(color, numbers.Integral):
        return color
    (r, g, b) = color_to_int(color)
    return (r << 16) | (g << 8) | b

def color_to_int(color):
    if isinstance(color, numbers.Integral):
        return (color >> 16, (color >> 8) & 0xff, color & 0xff)
    (r, g, b) = color
    if not isinstance(r, numbers.Integral):
        r = int(r * 256.0 - 0.5)
        g = int(g * 256.0 - 0.5)
        b = int(b * 256.0 - 0.5)
    return (r, g, b)

def color_to_float(color):
    if isinstance(color, numbers.Integral):
        r = color >> 16
        g = (color >> 8) & 0xff
        b = color & 0xff
    else:
        (r, g, b) = color
    if isinstance(r, numbers.Integral):
        r = (r + 0.5) / 256.0
        g = (g + 0.5) / 256.0
        b = (b + 0.5) / 256.0
    return (r, g, b)
