from flask import Blueprint, render_template, redirect, session, request, jsonify
from flask import current_app as app
from jukebox.src.util import *
import sqlite3, json, threading

playlist = Blueprint('playlist', __name__)


@playlist.route("/add", methods=['POST'])
@requires_auth
def add():
    """
    Ajoute l'url à la playlist
    """
    track = request.form.to_dict()
    print("adding", track)
    track["user"] = session["user"]
    with app.playlist_lock:
        app.playlist.append(track)
        conn = sqlite3.connect("jukebox.sqlite3")
        c = conn.cursor()
        c.execute("INSERT INTO log(track,user) VALUES (?,?)",
                  (json.dumps(track), session['user']))
        conn.commit()
        if len(app.playlist) == 1:
            threading.Thread(target=app.player_worker).start()
    return "ok"


@playlist.route("/remove", methods=['POST'])
@requires_auth
def remove():
    """supprime la track de la playlist"""
    track = request.form
    with app.playlist_lock:
        print("removing", track)
        for i in app.playlist:
            if i["url"] == track["url"]:
                if app.playlist.index(i) == 0:
                    app.player_skip.set()
                else:
                    app.playlist.remove(i)
                break
        else:
            print("not found !")
    return "ok"


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
        n = request.args.get("n")
    if n > 20:
        n = 20
    conn = sqlite3.connect("jukebox.sqlite3")
    c = conn.cursor()
    c.execute("SELECT track FROM log ORDER BY RANDOM() LIMIT ?;", (n, ))
    r = [json.loads(i[0]) for i in c.fetchall()]
    print(r)
    return jsonify(r)
