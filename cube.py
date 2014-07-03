#! /usr/bin/env python

# Framework for running LED cube demos
# Copyright (C) Paul Brook <paul@nowt.org>
# Released under the terms of the GNU General Public License version 3

import argparse
import itertools
import pkgutil
import time
import glcube
import serialcube

def load_patterns(cube):
    patterns = []
    for (finder, name, ispkg) in pkgutil.walk_packages(["patterns"]):
        print("Loading pattern module '%s'" % name)
        try:
            loader = finder.find_module(name)
            mod = loader.load_module(name)
            pclass = mod.Pattern
        except:
            print("Failed to load pattern '%s'" % name)
            pclass = None
        if pclass is not None:
            pobj = pclass(cube)
            patterns.append(pobj)
    if len(patterns) == 0:
        raise Exception("No patterns found")
    return itertools.cycle(patterns)

# Returns true to quit
def run_pattern(cube, pattern):
    interval = pattern.init()
    now = time.time()
    next_tick = now + interval
    expires = now + max_pattern_duration
    print("Running pattern %s" % pattern.name)
    while True:
        try:
            pattern.tick()
            if cube.render():
                return True
            now = time.time()
            if next_tick > now:
                time.sleep(next_tick - now)
            next_tick += interval
        except StopIteration:
            return False
        except KeyboardInterrupt:
            return True

ap = argparse.ArgumentParser(description="LED cube demo program")
ap.add_argument('-P', '--port', type=str,
        help="Serial port")
ap.add_argument('-s', '--size', type=int, default=8,
        help="Cube size")
args = ap.parse_args()

max_pattern_duration = 10
if args.port is None:
    c = glcube.Cube(args)
else:
    c = serialcube.Cube(args)
patterns = load_patterns(c)
while True:
    if run_pattern(c, next(patterns)):
        break;
c.clear()
c.render()
