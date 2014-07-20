import random
import numbers
import math

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
    
    if (math.fabs(to_y - from_y) > math.fabs(to_x - from_x)):
        # swap x and y
        from_x = to_point[1]
        from_y = to_point[0]
        to_x = from_point[1]
        to_y = from_point[0]
        xy_swapped = True

    #update the lists so next switch works too
    from_point = (from_x,from_y,from_z)
    to_point = (to_x,to_y,to_z)
    
    if (math.fabs(to_z - from_z) > math.fabs(to_x - from_x)):
        # swap x and z
        from_x = to_point[2]
        from_z = to_point[0]
        to_x = from_point[2]
        to_z = from_point[0]
        xz_swapped = True

    delta_x = math.fabs(to_x - from_x)
    delta_y = math.fabs(to_y - from_y)
    delta_z = math.fabs(to_z - from_z)

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

