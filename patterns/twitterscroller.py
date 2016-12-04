# Fork of scroller.py that tracks a twitter term
# Released under the terms of the GNU General Public License version 3

import cubehelper
import font
import random
import math
import tweepy
import json
import threading
import os

import Queue

# Twitter Authentication details. Obtain these visit dev.twitter.com,
# then set the corresponding ENV vars on launch

try:
    consumer_key = os.environ['TWITTER_CONSUMER_KEY']
    consumer_secret = os.environ['TWITTER_CONSUMER_SECRET']
    access_token = os.environ['TWITTER_ACCESS_TOKEN']
    access_token_secret = os.environ['TWITTER_ACCESS_TOKEN_SECRET']
    missing_auth = False
except KeyError:
    print "Please provide all four Twitter Authentication env vars"
    missing_auth = True
    pass

search_term = os.getenv('TWITTER_SEARCH_TERM', 'cube')

message_queue = Queue.Queue(maxsize=0)

def walker(cube):
    sz = cube.size - 1
    for y in range(sz, 0, -1):
        yield (0, y)
    for x in range(0, sz):
        yield (x, 0)
    for y in range(0, cube.size):
        yield (sz, y)

class Pattern(object):
    def init(self):
        if not missing_auth:
          self.streamThread = threading.Thread(target=self.setupStreamListener)
          self.streamThread.daemon = True
          self.streamThread.start()

        self.position = 0
        self.double_buffer = True
        self.pos = [pos for pos in walker(self.cube)]
        self.nextMessage()
        return 0.5 / self.cube.size
    def nextMessage(self):
        self.bitmap = [0] * len(self.pos)
        try:
            self.message = message_queue.get_nowait()
        except Queue.Empty:
            self.message = '...'
            pass
        self.color = cubehelper.random_color()
    def tick(self):
        self.cube.clear()
        while len(self.bitmap) < len(self.pos):
            if self.message == '':
                break;
            c = self.message[0]
            self.message = self.message[1:]
            n = ord(c) - 32
            if n >= 0 and n < len(font.font_data):
                self.bitmap.extend(font.font_data[n])
            self.bitmap.append(0)
        if len(self.bitmap) == 0:
            self.nextMessage()
            raise StopIteration
        for i in range(0, min(len(self.bitmap), len(self.pos))):
            mask = self.bitmap[i]
            (x, y) = self.pos[i]
            for z in range(0, 8):
                if mask & (0x80 >> z):
                    color = self.color
                else:
                    color = (0,0,0)
                self.cube.set_pixel((x, y, z), color)
        self.bitmap.pop(0)
    def setupStreamListener(self):
        l = StdOutListener()
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)

        print "Showing new tweets for " + search_term

        stream = tweepy.Stream(auth, l)
        stream.filter(track=[search_term])

class StdOutListener(tweepy.StreamListener):
    def on_data(self, data):
        decoded = json.loads(data)
        # convert UTF-8 to ASCII ignoring all bad characters sent by users
        print '@%s: %s' % (decoded['user']['screen_name'], decoded['text'].encode('ascii', 'ignore'))
        message_queue.put(decoded['text'].encode('ascii', 'ignore'))
        return True
    def on_error(self, status):
        print status

