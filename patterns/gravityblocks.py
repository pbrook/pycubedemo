from __future__ import with_statement
import cubehelper
import websocket
import json
import thread
import time
import copy
import numpy
from threading import Lock
from collections import defaultdict

class Pattern(object):
    def init(self):
        self.double_buffer = True

        if self.arg is None:
            print("Error: pass the address of the GravityBlocks server websocket in the format host:port")
            time.sleep(1)
            raise StopIteration

        self.MAX_PIXEL_COLOR = [255, 255, 255]

        self.pixels_lock = Lock()
        self.pixels_to_set = {key: [] for key in ['top', 'front', 'left', 'right', 'back', 'bottom']}

        # Define some queues of empty planes. Each face of the cube has a full cube's worth of planes, which are merged
        # together when rendered
        black = (0, 0, 0)
        size = self.cube.size

        self.facePlanes = {
            'top': FaceHistory(self.cube.size, 'top', [[black for i in range(0, size)] for j in range(0, size)]),
            'front': FaceHistory(self.cube.size, 'front', [[black for i in range(0, size)] for j in range(0, size)]),
            'left': FaceHistory(self.cube.size, 'left', [[black for i in range(0, size)] for j in range(0, size)]),
            'right': FaceHistory(self.cube.size, 'right', [[black for i in range(0, size)] for j in range(0, size)]),
            'back': FaceHistory(self.cube.size, 'back', [[black for i in range(0, size)] for j in range(0, size)]),
            'bottom': FaceHistory(self.cube.size, 'bottom', [[black for i in range(0, size)] for j in range(0, size)])
        }

        self.colors = [] # set when the welcome message is received

        self.ews = EventedWebsocket("ws://%s/" % self.arg)
        self.ews.attach_handler('open', self.on_open)
        self.ews.attach_handler('welcome', self.on_welcome)
        self.ews.attach_handler('activate', self.on_activate)
        self.ews.attach_handler('deactivate', self.on_deactivate)
        self.ews.connect()

        return 1.0/15

    def tick(self):
        print("tick")
        with self.pixels_lock:
            for face, planes in self.facePlanes.iteritems():
                new_plane = copy.deepcopy(planes[0])

                print("face " + face)
                print("new plane before changes")
                print(numpy.array_str(new_plane))

                # apply all requested pixel changes from the other thread to the new front plane of the specified face
                for (coord, color) in self.pixels_to_set[face]:
                    new_plane[coord[0]][coord[1]] = color
                self.pixels_to_set[face] = []

                print("new plane after changes")
                print(numpy.array_str(new_plane))

                planes.prepend(new_plane)

        # render planes to cube
        merged = self.merge_planes(self.facePlanes)
        for y in range(0, self.cube.size):
            for x in range(0, self.cube.size):
                for z in range(0, self.cube.size):
                    self.cube.set_pixel((x, y, z), cubehelper.color_to_float(merged[x][y][z]))

        # self.cube.set_pixel((1, 2, 3), (1.0, 1.0, 1.0))

    def merge_planes(self, faces):
        """Take an array of faces, each of which is an array of planes, and merge them into one 3D array of pixels, taking into
        account the view perspective of the original faces. This sounds mad, but yes, this does mean that each face has an
        entire cube's worth of pixels. I'll probably change this to use a particle system at some point."""

        # Array to store merged colours in. 3D array with a fourth array dimension for the R, G, B components.
        computed = numpy.empty([self.cube.size, self.cube.size, self.cube.size, 3], dtype=float)

        # For each of the 6 cubes (one from each face), get the colour of the same pixel on each and merge them together
        for x in range(self.cube.size):
            for y in range(self.cube.size):
                for z in range(self.cube.size):
                    # Index the array with y coord at the start, to optimise outputting serial data to the cube
                    faceColours = [f.get_from_front_perspective(x, y, z) for f in faces.values()]
                    mixed = numpy.sum(faceColours, axis=0) # R, G, B array
                    computed[x][y][z] = numpy.minimum(mixed, self.MAX_PIXEL_COLOR)

        return computed


    def on_open(self):
        print("Connected to GravityBlocks server")
        self.ews.emit("hello")

    def on_welcome(self, data):
        if (data["app"] != "GravityBlocks"):
            print("Error: this isn't a GravityBlocks server! We're gonna do jack all about it though because we're lazy")
        else:
            self.colors = data["colors"]
            print("Successfully handshaken with server")

    def on_activate(self, data):
        with self.pixels_lock:
            col = tuple(self.colors[data["color"]])
            print("on_activate")
            print("data: " + json.dumps(data))
            translated_coords = self.translate_coords(data["coords"]["x"], data["coords"]["y"])
            print("translated: " + json.dumps(translated_coords))
            self.pixels_to_set[data["face"]].append((translated_coords, col))

    def on_deactivate(self, data):
        with self.pixels_lock:
            self.pixels_to_set[data["face"]].append((self.translate_coords(data["coords"]["x"], data["coords"]["y"]), (0, 0, 0)))

    def translate_coords(self, x, y):
        """ Translate finger-coordinates (i.e. top left is 0, 0, bottom left is 0, 7) to plane coords (i.e. top left
            is 0, 7, bottom left is 0, 0). Plane coords use x and y axes """
        return (x, self.cube.size - y - 1)

class EventedWebsocket(object):
    def __init__(self, url):
        self.event_handlers = defaultdict(list)
        self.connect_url = url

    def connect(self):
        self.ws = websocket.WebSocketApp(self.connect_url,
                            on_message = self.on_message,
                            on_error = self.on_error,
                            on_open = self.on_open,
                            on_close = self.on_close)
        thread.start_new_thread(self.ws.run_forever, ())

    def emit(self, event, data=None):
        if data == None:
            self.ws.send(event)
        else:
            self.ws.send(event + "|" + json.dumps(data))

    def attach_handler(self, event, callable):
        self.event_handlers[event].append(callable)

    def run_handlers(self, event, *args):
        for handler in self.event_handlers[event]:
            handler(*args)

    def on_message(self, ws, message):
        """
        Handle an incoming websocket message. Our protocol will either send a string on its
        own, in which case it's just an event, or it will be in the format
        eventname|{'optional': 'jsondata'} which is an event with a JSON data payload
        """

        self.run_handlers("message", message)

        parts = message.split("|", 1)
        if len(parts) == 1:
            self.run_handlers(parts[0])
        else:
            self.run_handlers(parts[0], json.loads(parts[1]))

    def on_error(self, ws, error):
        self.run_handlers("error", error)

    def on_open(self, ws):
        self.run_handlers("open")

    def on_close(self, ws):
        self.run_handlers("close")

class FaceHistory(object):
    """Similar to a simplified deque but with O(1) random access instead of O(n). Represents
    a 3D cube made up of planes, each of which is an item in a queue. New planes can be pushed
    (prepended) to the front of the queue, pushing old items off the end."""

    def __init__(self, size, face, initVal):
        self.size = size
        self.face = face
        self.contents = [initVal] * size
        self.head_pointer = 0

    def prepend(self, item):
        """Insert an item at the start of the queue. An item will be pushed off the end of the queue."""
        new_head_pointer = self._wrap_into_valid_range(self.head_pointer - 1)
        self.head_pointer = new_head_pointer
        self.contents[new_head_pointer] = item

    def get_from_front_perspective(self, x, y, z):
        """Get an item from the cube, with the coordinates passed in from the front of the cube's perspective.
        Returns an array of R, G, B components between 0 and 255"""
        translated = self._translate_from_front_to(self.face, x, y, z)
        return self[translated[0]][translated[1]][translated[2]] 

    def _translate_from_front_to(self, perspective, x, y, z):
        """Translate a coordinate passed in from the perspective of the front of the cube to the specified perspective.
        TODO: replace hardcoded cube size with something better"""
        if self.face == "front":
            return [x, y, z]
        elif self.face == "back":
            return [7-x, 7-y, z]
        elif self.face == "left":
            return [7-y, x, z]
        elif self.face == "right":
            return [y, 7-x, z]
        elif self.face == "top":
            return [x, 7-z, y]
        elif self.face == "bottom":
            return [x, z, 7-y]

    # top in,      out
    # 0, 0, 0      0, 7, 0
    # 1, 1, 1      1, 6, 1
    # 0, 3, 0      0, 7, 3
    # 1, 2, 3      1, 4, 2

    def _wrap_into_valid_range(self, pointer):
        """Take a pointer index and return it mapped into the valid range for the queue"""
        return (pointer + self.size) % self.size

    def __getitem__(self, index):
        if index >= self.size:
            raise IndexError

        return self.contents[self._wrap_into_valid_range(self.head_pointer + index)]

    def __len__(self):
        return self.size
