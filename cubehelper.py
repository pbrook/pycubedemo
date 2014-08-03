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

def random_color(other_color=(-1, -1, -1)):
    """Return a random color as a float tuple, optionally ensuring that it is different to the other_color parameter."""

    r = 0
    g = 0
    b = 0

    (other_r, other_g, other_b) = [int(x + 0.5) for x in color_to_float(other_color)]

    while (r == 0 and g == 0 and b == 0) or (r == other_r and g == other_g and b == other_b):
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

# WARN: rounding behaviour isn't perfect, eg
#   >>> cubehelper.color_to_float((0,0,0))
#   (0.001953125, 0.001953125, 0.001953125)
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

# in 3d space any floating coord lies between 8 pixels (or exactly on/between)
# return a list of the surrounding 8 pixels with the color scaled proportionately
# ie list of 8x ((x,y,z), (r,g,b))
# Due to the rounding issues in color_to_float we end up with values where
# we'd expect 0 (which would allow us to clean up black pixels)
def interpolated_pixels_from_point(xyz, color):
    (x, y, z) = xyz

    x0 = int(x)
    y0 = int(y)
    z0 = int(z)

    x1 = x0 + 1
    y1 = y0 + 1
    z1 = z0 + 1

    # weightings on each axis
    x1w = x - x0
    y1w = y - y0
    z1w = z - z0

    x0w = 1 - x1w
    y0w = 1 - y1w
    z0w = 1 - z1w

    # weighting for each of the pixels
    c000w = x0w * y0w * z0w
    c001w = x0w * y0w * z1w
    c010w = x0w * y1w * z0w
    c011w = x0w * y1w * z1w
    c100w = x1w * y0w * z0w
    c101w = x1w * y0w * z1w
    c110w = x1w * y1w * z0w
    c111w = x1w * y1w * z1w

    black = (0,0,0)

    c000 = mix_color(black, color, c000w)
    c001 = mix_color(black, color, c001w)
    c010 = mix_color(black, color, c010w)
    c011 = mix_color(black, color, c011w)
    c100 = mix_color(black, color, c100w)
    c101 = mix_color(black, color, c101w)
    c110 = mix_color(black, color, c110w)
    c111 = mix_color(black, color, c111w)

    return [
      ((x0, y0, z0), c000),
      ((x0, y0, z1), c001),
      ((x0, y1, z0), c010),
      ((x0, y1, z1), c011),
      ((x1, y0, z0), c100),
      ((x1, y0, z1), c101),
      ((x1, y1, z0), c110),
      ((x1, y1, z1), c111)
    ]

# This doesn't check for negative coords
def restrict_pixels_to_cube_bounds(pixels, cube_size):
    return [
        pixel for pixel in pixels if (
            pixel[0][0] < cube_size and
            pixel[0][1] < cube_size and
            pixel[0][2] < cube_size )
    ]

def restrict_pixels_to_non_black(pixels):
    threshold = 0.002 # this is mostly to work round the rounding issue above
    return [
        pixel for pixel in pixels if (
            pixel[1][0] > threshold and
            pixel[1][1] > threshold and
            pixel[1][2] > threshold )
    ]

# provide xyz as float coords, returns a list of between one and 8 pixels
def sanitized_interpolated(xyz, color, cube_size):
    return restrict_pixels_to_non_black(
             restrict_pixels_to_cube_bounds(
                interpolated_pixels_from_point(xyz, color),
                cube_size
           ))