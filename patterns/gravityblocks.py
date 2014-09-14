from __future__ import with_statement
import cubehelper
import websocket
import json
import thread
import time
from threading import Lock
from collections import defaultdict

class Pattern(object):
    def init(self):
        if self.arg is None:
            print("Error: pass the address of the GravityBlocks server websocket in the format host:port")
            time.sleep(1)
            raise StopIteration

        self.pixels_lock = Lock()
        self.pixels_to_set = []

        self.colors = [] # set when the welcome message is received

        self.ews = EventedWebsocket("ws://%s/" % self.arg)
        self.ews.attach_handler('open', self.on_open)
        self.ews.attach_handler('welcome', self.on_welcome)
        self.ews.attach_handler('activate', self.on_activate)
        self.ews.attach_handler('deactivate', self.on_deactivate)
        self.ews.connect()

        return 1.0/30

    def tick(self):
        with self.pixels_lock:
            for (coord, color) in self.pixels_to_set:
                self.cube.set_pixel(coord, color)
            self.pixels_to_set = []

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
            col = cubehelper.color_to_float(self.colors[data["color"]])
            self.pixels_to_set.append((self.translate_coords(data["coords"]["x"], data["coords"]["y"]), col))

    def on_deactivate(self, data):
        with self.pixels_lock:
            self.pixels_to_set.append((self.translate_coords(data["coords"]["x"], data["coords"]["y"]), (0.0, 0.0, 0.0)))

    def translate_coords(self, x, y):
        """ Translate finger-coordinates (i.e. top left is 0, 0, bottom left is 0, 7) to cube front face coords """
        return (y, 0, self.cube.size - x - 1)

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
