import random
import numbers

def random_color():
    r = 0
    g = 0
    b = 0
    while r == 0 and g == 0 and b == 0:
        r = random.randrange(2)
        g = random.randrange(2)
        b = random.randrange(2)
    return (float(r), float(g), float(b))

def scale_color(color, level):
    (r, g, b) = color
    return (r * level, g * level, b * level)

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
