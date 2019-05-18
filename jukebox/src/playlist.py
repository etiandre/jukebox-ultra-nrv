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
    track = request.form.to_dict()
    app.logger.info("Adding track %s", track["url"])
    track["user"] = session["user"]
    with app.database_lock:
        conn = sqlite3.connect(app.config["DATABASE_PATH"])
        c = conn.cursor()
        # check if track not in track_info i.e. if url no already there
        c.execute("""select id
                     from track_info
                     where url = ?;
                  """,
                  (track["url"],))
        r = c.fetchall()
        if not r:
            c.execute("""INSERT INTO track_info
                    (url, track, artist, album, duration, albumart_url,
                    source) VALUES
                    (?,   ?,     ?,      ?,     ?,        ?,
                    ?)
                    ;""",
                      (track["url"], track["title"], track["artist"],
                       track["album"], track["duration"],
                       track["albumart_url"], track["source"]))
            # get id
            c.execute("""select id
                         from track_info
                         where url = ?;
                      """,
                      (track["url"],))
            r = c.fetchall()
            track_id = r[0][0]
        else:
            track_id = r[0][0]

        # print("User: " + str(session['user']))
        c.execute("""select id
                     from users
                     where user = ?;
                  """,
                  (session['user'],))
        r = c.fetchall()
        # print(r)
        user_id = r[0][0]
        c.execute("INSERT INTO log(trackid,userid) VALUES (?,?)",
                  (track_id, user_id))
        conn.commit()
    # app.mpv.playlist_append(track["url"])
    with app.playlist_lock:
        app.playlist.append(track)
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
            if track_p["url"] == track["url"]:
                if app.playlist.index(track_p) == 0:
                    app.logger.info("Removing currently playing track")
                    with app.mpv_lock:
                        # app.mpv.stop()
                        # app.mpv.command(["set_property", "pause", True])
                        app.mpv.quit()
                        # app.mpv.terminate()
                        # app.mpv = "unavailable"
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
