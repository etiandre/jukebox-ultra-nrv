# -*- coding: utf-8 -*-
import threading
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


import subprocess,time
def player_worker():
    print("starting player")
    while len(app.playlist) > 0:
        print("playing {}".format(app.playlist[0]))
        player = None
        if app.playlist[0]["source"] == "youtube":
            player = subprocess.Popen(["mpv", "--no-video", "--quiet", app.playlist[0]["url"]], stdin=subprocess.DEVNULL)
        while player.poll() is None and not app.player_skip.is_set():
            time.sleep(0.1)
        player.kill()
        app.player_skip.clear()
        with app.playlist_lock:
            del(app.playlist[0])
    print("stopping player")

app.player_worker=player_worker
