# -*- coding: utf-8 -*-
import threading
import time

import logging

from flask import Flask

from jukebox.src.MyMPV import MyMPV
from jukebox.src.Track import Track
from jukebox.src.main import main
from jukebox.src.auth import auth
from jukebox.src.playlist import playlist

import importlib


class Jukebox(Flask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.WARNING)
        with open("version.txt", 'r') as f:
            self.version = f.read()

        self.mpv = None
        self.currently_played = None
        self.mpv_lock = threading.Lock()
        self.database_lock = threading.Lock()
        self.stylesheet = "default.css"
        self.config.from_pyfile("../config.py")
        self.register_blueprint(main)
        self.register_blueprint(auth)
        self.register_blueprint(playlist)

        self.playlist_lock = threading.Lock()
        self.playlist = []
        self.player_skip = threading.Event()
        self.player_time = 0

        # Load backends

        self.search_backends = []
        for i in self.config["SEARCH_BACKENDS"]:
            self.search_backends.append(importlib.import_module("jukebox.src.backends.search." + i))

    def player_worker(self):
        while len(self.playlist) > 0:
            url = self.playlist[0]["url"]
            self.currently_played = url
            with app.mpv_lock:
                if hasattr(self, 'mpv') and self.mpv:
                    del self.mpv
                self.mpv = MyMPV(None)  # we start the track
            start = time.time()
            end = start
            with self.database_lock:
                track = Track.import_from_url(app.config["DATABASE_PATH"], url)
            counter = 0
            # duration of track
            while counter < 5 and track.duration is not None and end - start < min(track.duration, 10):
                # note for the future : what if track is passed with a timestamp ?
                start = time.time()
                with app.mpv_lock:
                    self.mpv.play(self.currently_played)
                # the next instruction should be the only one without a lock
                # but it causes a segfault
                # I fear fixing it may be dirty
                # we could switch to mpv playlists though
                self.mpv.wait_for_playback()  # it's stuck here while it's playing
                end = time.time()
                counter += 1
            with self.mpv_lock:
                del self.mpv  # the track is finished
                # self.mpv = "unavailable"  # or del app.mpv
            with self.playlist_lock:
                if len(self.playlist) > 0 and url == self.currently_played:
                    del self.playlist[0]


app = Jukebox(__name__)
