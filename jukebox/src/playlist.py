from flask import Blueprint, request, jsonify

from jukebox.src.Track import Track
from jukebox.src.util import *
import sqlite3
import threading

from mpv import MpvEventID

playlist = Blueprint('playlist', __name__)


@playlist.route("/add", methods=['POST'])
@requires_auth
def add():
    """
    Ajoute l'url à la playlist
    """
    track_dict = request.form.to_dict()
    app.logger.info(track_dict)
    app.logger.info("Adding track %s", track_dict["url"])
    # track["user"] = session["user"]
    with app.database_lock:
        if not Track.does_track_exist(app.config["DATABASE_PATH"], track_dict["url"]):
            Track.insert_track(app.config["DATABASE_PATH"], track_dict)
        track = Track.import_from_url(app.config["DATABASE_PATH"], track_dict["url"])
        if track is not None:
            track.insert_track_log(app.config["DATABASE_PATH"], session['user'])
        else:
            app.logger.warning("Track is None !")
            return "nok"

    with app.playlist_lock:
        app.playlist.append(track.serialize())
        if len(app.playlist) == 1:
            threading.Thread(target=app.player_worker).start()
    return "ok"


@playlist.route("/remove", methods=['POST'])
@requires_auth
def remove():
    """supprime la track de la playlist"""
    track = request.form
    with app.playlist_lock:
        for track_p in app.playlist:
            if track_p["randomid"] == int(track["randomid"]):
                if app.playlist.index(track_p) == 0:
                    app.logger.info("Removing currently playing track")
                    # app.logger.info(track)
                    with app.mpv_lock:
                        # app.mpv.stop()
                        # app.mpv.command(["set_property", "pause", True])
                        app.mpv.quit()
                        # app.mpv.terminate()
                        # app.mpv = "unavailable
                else:
                    app.playlist.remove(track_p)
                # app.playlist_skip.set()
                return "ok"
    app.logger.info("Track " + track["url"] + " not found !")
    return "nok"


@playlist.route("/volume", methods=['POST'])
@requires_auth
def volume():
    if request.method == 'POST':
        set_volume(request.form["volume"])
        return "ok"


@playlist.route("/suggest")
def suggest():
    n = 5
    if "n" in request.args:
        n = int(request.args.get("n"))
    # if n > 20:
    #    n = 20
    result = []
    nbr = 0
    while nbr < n:  # we use a while to be able not to add a song
        # if it is blacklisted
        with app.database_lock:
            track = Track.get_random_track(app.config["DATABASE_PATH"])
        if track is None:
            nbr += 1
        elif track.blacklisted == 0 and track.source in app.config["SEARCH_BACKENDS"]:
            result.append(track.serialize())
            nbr += 1
    return jsonify(result)
