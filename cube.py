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

def load_patterns(cube, match):
    patterns = {}
    for (finder, name, ispkg) in pkgutil.walk_packages(["patterns"]):
        if match is not None and name not in match:
            continue
        print("Loading pattern module '%s'" % name)
        try:
            loader = finder.find_module(name)
            mod = loader.load_module(name)
            constructor = mod.Pattern
        except Exception as e:
            print e
            print("Failed to load pattern '%s'" % name)
            constructor = None
        if constructor is not None:
            pobj = constructor()
            pobj.name = name
            pobj.cube = cube
            patterns[name] = pobj
    if len(patterns) == 0:
        raise Exception("No patterns found")
    if match is None:
        ordered = patterns.itervalues()
    else:
        ordered = map(lambda x: patterns[x], match)
    return itertools.cycle(ordered)

# Returns true to quit
def run_pattern(cube, pattern):
    interval = pattern.init()
    now = time.time()
    next_tick = now + interval
    if args.interval > 0:
        expires = now + args.interval
    else:
        expires = None
    print("Running pattern %s" % pattern.name)
    cube.clear()
    while True:
        try:
            pattern.tick()
            if cube.render():
                return True
            now = time.time()
            if expires is not None and now > expires:
                raise StopIteration
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
ap.add_argument('-p', '--pattern', type=str, action='append',
        help="Patterns to run")
ap.add_argument('-i', '--interval', type=float, default=10.0,
        help="Maximum interval between patterns")
args = ap.parse_args()

if args.port is None:
    c = glcube.Cube(args)
else:
    c = serialcube.Cube(args)
if args.pattern is None:
    plist = None
else:
    plist = ','.join(args.pattern).split(',')
patterns = load_patterns(c, plist)
while True:
    if run_pattern(c, next(patterns)):
        break;
c.clear()
c.render()
