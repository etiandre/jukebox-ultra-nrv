# -*- coding: utf-8 -*-
import threading
import time

import logging

from flask import Flask

from jukebox.src.MyMPV import MyMPV
from jukebox.src.main import main
from jukebox.src.auth import auth
from jukebox.src.playlist import playlist

import importlib


class Jukebox(Flask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mpv = None
        self.currently_played = None


    # create player worker
    def player_worker(self):
        while len(self.playlist) > 0:
            self.currently_played = self.playlist[0]["url"]
            self.mpv = MyMPV(None)  # we start the track
            self.mpv.play(self.currently_played)
            self.mpv.wait_for_playback()  # it's stuck here while it's playing
            self.mpv.terminate() # the track is finished
            with self.playlist_lock:
                if len(self.playlist) > 0 and self.playlist[0]["url"] == self.currently_played:
                    del self.playlist[0]


app = Jukebox(__name__)

app.config.from_pyfile("../config.py")
app.register_blueprint(main)
app.register_blueprint(auth)
app.register_blueprint(playlist)

app.playlist_lock = threading.Lock()
app.playlist = []
app.player_skip = threading.Event()
app.player_time = 0
log = logging.getLogger('werkzeug')
log.setLevel(logging.WARNING)

# Load backends

app.search_backends = []
for i in app.config["SEARCH_BACKENDS"]:
    app.search_backends.append(importlib.import_module("jukebox.src.backends.search." + i))