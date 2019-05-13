from flask import Blueprint, request, jsonify
from jukebox.src.util import *
import sqlite3
import threading

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
    #print(track["url"])
    conn = sqlite3.connect(app.config["DATABASE_PATH"])
    c = conn.cursor()
    # check if track not in track_info i.e. if url no already there
    c.execute("""select id
                 from track_info
                 where url = ?;
              """,
    (track["url"],))
    r = c.fetchall()
    if r == []:
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

    #print("User: " + str(session['user']))
    c.execute("""select id
                 from users
                 where user = ?;
              """,
    (session['user'],))
    r = c.fetchall()
    #print(r)
    user_id = r[0][0]
    c.execute("INSERT INTO log(trackid,userid) VALUES (?,?)",
              (track_id, user_id))
    conn.commit()
    #app.mpv.playlist_append(track["url"])
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
                    #app.logger.info("Removing currently playing track")
                    app.mpv.terminate()
                app.playlist.remove(track_p)
                #app.playlist_skip.set()
                return "ok"
    app.logger.info("Track " + track["url"] + " not found !")
    return "nok"


@playlist.route("/volume", methods=['POST'])
@requires_auth
def volume():
    if request.method == 'POST':
        subprocess.run([
            'amixer', '-q', 'set', "'Master',0", request.form["volume"] + "%"
        ])
        app.logger.info("Volume set to %s", request.form["volume"])
        return "ok"


@playlist.route("/suggest")
def suggest():
    n = 5
    if "n" in request.args:
        n = int(request.args.get("n"))
    #if n > 20:
    #    n = 20
    result = []
    conn = sqlite3.connect(app.config["DATABASE_PATH"])
    c = conn.cursor()
    nbr = 0
    while nbr < n: # we use a while to be able not to add a song
        # if it is blacklisted
        c.execute("SELECT * FROM log ORDER BY RANDOM() LIMIT 1;")
        r_log = c.fetchall()
        track_id = r_log[0][1]
        user_id = r_log[0][2]
        c.execute("SELECT user FROM users WHERE id = ?;", (user_id,))
        r = c.fetchall()
        user = r[0][0]
        c.execute("SELECT * FROM track_info WHERE id = ?;", (track_id,))
        r = c.fetchall()
        #track_tuple = r[0]
        for track_tuple in r:
            #app.logger.info("nbr : " + str(nbr))
            source = track_tuple[7]
            # 0 means it is not blacklisted
            if track_tuple[8] == 0 and \
                    source in app.config["SEARCH_BACKENDS"]:
                # TODO : check that it the source is loaded
                result.append({
                    "albumart_url": track_tuple[6],
                    "title": track_tuple[2],
                    "artist": track_tuple[3],
                    "duration": track_tuple[5],
                    "source": source,
                    "user": user,
                    "url": track_tuple[1]
                        })
                nbr += 1
    #app.logger.info(jsonify(result))
    return jsonify(result)
