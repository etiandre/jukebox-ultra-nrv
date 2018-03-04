# -*- coding: utf-8 -*-
import threading, time

from flask import Flask
from jukebox.src.main import main
from jukebox.src.auth import auth
from jukebox.src.playlist import playlist
app = Flask(__name__)
app.register_blueprint(main)
app.register_blueprint(auth)
app.register_blueprint(playlist)

app.playlist_lock = threading.Lock()
app.playlist = []
app.player_skip = threading.Event()
app.player_time = 0
import subprocess, time

import jukebox.src.mpv as mpv
class MyMPV(mpv.MPV):
    def __init__(self, path):
        super().__init__(window_id=None, debug=False)

        self.command("loadfile", path, "append")
        self.set_property("playlist-pos", 0)
        self.loaded = threading.Event()
        self.loaded.wait()

    def on_file_loaded(self):
        self.loaded.set()

    def on_property_time_pos(self, position=None):
        if position is None:
            return
        app.player_time = position

    def pos(self):
        return self.get_property("time-pos")
    def finished(self):
        r = None
        try:
            r=self.get_property("eof-reached")
            return r
        except (mpv.MPVCommandError, BrokenPipeError):
            return True
    def play(self):
        self.set_property("pause", False)

    def pause(self):
        self.set_property("pause", True)

    def seek(self, position):
        self.command("seek", position, "absolute")

def player_worker():
    print("starting player")
    while len(app.playlist) > 0:
        print("playing {}".format(app.playlist[0]))
        player = None
        if app.playlist[0]["source"] == "youtube":
            app.mpv = MyMPV(app.playlist[0]["url"])
        while not app.mpv.finished():
            time.sleep(0.5)
        del(app.mpv)
        with app.playlist_lock:
            del (app.playlist[0])
    print("stopping player")


app.player_worker = player_worker
