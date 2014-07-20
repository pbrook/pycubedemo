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

def mix_color(color0, color1, level):
    f0 = color_to_float(color0)
    f1 = color_to_float(color1)
    return tuple([f1[n] * level + f0[n] * (1.0 - level) for n in range(0, 3)])

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

def line_to_points(from_point,to_point):
    # Converted 3d Bresenham's algo from Pascal at http://cobrabytes.squeakyduck.co.uk/forum/index.php?topic=1150.0
    points = []
    xy_swapped = False
    xz_swapped = False

    (from_x, from_y, from_z) = from_point
    (to_x, to_y, to_z) = to_point
    
    if (abs(to_y - from_y) > abs(to_x - from_x)):
        # swap x and y
        from_x = from_point[1]
        from_y = from_point[0]
        to_x = to_point[1]
        to_y = to_point[0]
        xy_swapped = True

    #update the lists so next switch works too
    from_point = (from_x,from_y,from_z)
    to_point = (to_x,to_y,to_z)
    
    if (abs(to_z - from_z) > abs(to_x - from_x)):
        # swap x and z
        from_x = from_point[2]
        from_z = from_point[0]
        to_x = to_point[2]
        to_z = to_point[0]
        xz_swapped = True

    delta_x = abs(to_x - from_x)
    delta_y = abs(to_y - from_y)
    delta_z = abs(to_z - from_z)

    drift_xy = drift_xz = delta_x/2

    step_x = step_y = step_z = 1
    if (from_x > to_x):
        step_x = -1
    if (from_y > to_y):
        step_y = -1
    if (from_z > to_z):
        step_z = -1

    y = from_y
    z = from_z

    for x in range(from_x, to_x+step_x, step_x):
        copy = [x,y,z]

        if xz_swapped:
            copy[0] = z
            copy[2] = x
            (x,y,z) = copy

        if xy_swapped:
            copy[0] = y
            copy[1] = x
            (x,y,z) = copy

        yield (x,y,z)

        drift_xy -= delta_y
        drift_xz -= delta_z

        if drift_xy < 0:
            y = y + step_y
            drift_xy += delta_x

        if drift_xz < 0:
            z = z + step_z
            drift_xz += delta_x

