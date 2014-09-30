#! /usr/bin/env python

# Framework for running LED cube demos
# Copyright (C) Paul Brook <paul@nowt.org>
# Released under the terms of the GNU General Public License version 3

import argparse
import itertools
import pkgutil
import time
import signal
import cubehelper
import random

pattern_details = [
    # name, args, duration
    ('plasma', '', 15),
    ('boxflip', '', 10),
    ('cubezoom','',10),
    ('spiral','',10),
    ('fireworks','',10),
    ('cubefill','',10),
    ('swipe','',10),
    ('wave','',10),
    ('fade','',10),
    ('worm','',10),
]

def load_patterns(cube, details):
    patterns = {}
    arglist = {}
    for d in details:
        patterns[d[0]] = None
    for (finder, name, ispkg) in pkgutil.walk_packages(["patterns"]):
        if name not in patterns:
            continue
        print("Loading pattern module '%s'" % name)
        try:
            loader = finder.find_module(name)
            mod = loader.load_module(name)
            patterns[name] = mod.Pattern
        except Exception as e:
            print(e)
            raise Exception("Failed to load pattern '%s'" % name)
    ordered = []
    for (name, args, duration) in details:
        pobj = patterns[name]()
        pobj.name = name
        pobj.cube = cube
        pobj.arg = args
        pobj.duration = duration
        ordered.append(pobj)
    return itertools.cycle(ordered)

# Returns true to quit
def run_pattern(cube, pattern, expires):
    try:
        interval = pattern.init()
        now = time.time()
        next_tick = now + interval
        sec_tick = now + 1.0
        frames = 0
        print("Running pattern %s" % pattern.name)
        while True:
            try:
                pattern.tick()
            except StopIteration:
                if now >= expires:
                    raise
            cube.render()
            cube.swap()
            now = time.time()
            if next_tick > now:
                time.sleep(next_tick - now)
            next_tick += interval
            frames += 1
            if now >= sec_tick:
                if debug_frames:
                    print("%d/%d" % (frames, int(1.0/interval)))
                sec_tick += 1.0
                frames = 0
    except StopIteration:
        return

def sigterm_handler(_signo, _stack_frame):
    raise KeyboardInterrupt

ap = argparse.ArgumentParser(description="LED cube demo program")
ap.add_argument('-P', '--port', type=str,
        help="Serial port")
ap.add_argument('-s', '--size', type=int, default=8,
        help="Cube size")
ap.add_argument('-f', '--frames', action='store_true', default=False,
        help="Display framerate")
args = ap.parse_args()

debug_frames = args.frames
if args.port is None:
    import glcube
    c = glcube.Cube(args)
else:
    import serialcube
    c = serialcube.Cube(args)

c.plasma = cubehelper.color_plasma

try:
    #c.set_brightness((8, 4, 4))
    #c.set_brightness((0xc0, 0xff, 0xff))
    c.set_brightness((0x30, 0x45, 0x40))
    #c.set_brightness((0x10, 0x08, 0x08))
except:
    pass

signal.signal(signal.SIGTERM, sigterm_handler)

patterns = load_patterns(c, pattern_details)
try:
    expires = time.time()
    for p in patterns:
        expires += p.duration
        run_pattern(c, p, expires)
except KeyboardInterrupt:
    pass
c.single_buffer()
c.clear()
c.render()
