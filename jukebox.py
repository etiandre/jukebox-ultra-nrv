# -*- coding: utf-8 -*-
import os
import json
import requests
import mac_auth
import time
import sqlite3
import hashlib
import threading
import subprocess
import time
import re
from functools import wraps
from flask import Flask, render_template, session, request, redirect, jsonify, flash
from config import CONFIG

maclist_lock = threading.Lock()
maclist = []
app = Flask(__name__)
app.secret_key = CONFIG["secret_key"]
playlist_lock = threading.Lock()
playlist = []
player_skip = threading.Event()

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session or session['user'] is None:
            app.logger.info("Unauthorized attempt")
            return redirect("/auth")
        return f(*args, **kwargs)
    return decorated

##########################################################################################

@app.route("/app")
@requires_auth
def main():
    app.logger.info("App access from %s %s", session["user"], session["mac"])
    return render_template("accueil.html", user=session["user"], mac=session["mac"])

@app.route("/auth", methods=['GET','POST'])
def auth():
    conn = sqlite3.connect("jukebox.sqlite3")
    c = conn.cursor()
    mac = mac_auth.get_mac(request.remote_addr)
    session["mac"] = mac
    
    if request.method == 'GET':
        # if already logged
        if "user" in session and session['user'] is not None:
            return redirect("/app") 
        c.execute("SELECT * FROM macs WHERE mac=?", (session["mac"],))
        r = c.fetchone()
        # if mac saved
        if r is not None:
            session["user"] = r[0]
            return redirect("/app")
        else:
            return render_template("auth.html")
    
    success=False
    if request.form["action"] == "new":
        try:
            c.execute('INSERT INTO users VALUES (?,?)',(
                request.form["user"],
                hashlib.sha512(request.form["pass"].encode()).hexdigest()
            ))
            conn.commit()
            app.logger.info("Created account for %s", request.form["user"])
            success=True
        except sqlite3.IntegrityError:
            app.logger.info("Account already exists for %s", request.form["user"])
            flash("T'as déjà un compte gros malin")
    else:
        c.execute("SELECT user FROM users WHERE user=? AND pass=?",(
            request.form["user"],
            hashlib.sha512(request.form["pass"].encode()).hexdigest()
        ))
        if c.fetchone() != None:
            app.logger.info("Logging in %s using password", request.form["user"])
            success=True
        else:
            flash("Raté")
            app.logger.info("Failed log attempt for %s", request.form["user"])
    if success == True:
        session['user'] = request.form['user']
        c.execute("REPLACE INTO macs (user, mac) VALUES (?,?)",(
            request.form["user"],
            session["mac"]
        ))
        conn.commit()
        return redirect("/app")
    return render_template("auth.html")
  
@app.route("/logout", methods=['GET', 'POST'])
@requires_auth
def logout():
    if request.method == "POST":
        app.logger.info("Unassociating %s and %s", session['user'], session['mac'])
        conn = sqlite3.connect("jukebox.sqlite3")
        c = conn.cursor()
        c.execute("DELETE FROM macs WHERE user=? AND mac=?",(
            session["user"],
            session["mac"]
        ))
        conn.commit()
        session['user'] = None
        session['mac'] = None
        return redirect("/auth")
    else:
        return render_template("logout.html", user=session["user"])
@app.route("/")
def accueil():
    return redirect("/app")

##########################################################################################
def player_worker():
    global playlist, playlist_lock
    print("starting player")
    while len(playlist) > 0:
        print("playing {}".format(playlist[0]))
        player = None
        if playlist[0]["source"] == "youtube":
            player = subprocess.Popen(["mpv", "--no-video", "--quiet", playlist[0]["url"]], stdin=subprocess.DEVNULL)
        while player.poll() is None and not player_skip.is_set():
            time.sleep(0.1)
        player.kill()
        player_skip.clear()
        with playlist_lock:
            del(playlist[0])
    print("stopping player")
@app.route("/sync")
def sync():
    """
    Renvoie quelque choise du type vnr
    """
    # récupération du temps écoulé
    elapsed = 0
    res = {
        "playlist": playlist,
        "time": elapsed, # temps actuel
        "maclist": maclist,
    }

    return jsonify(res)

@app.route("/search", methods=['POST'])
@requires_auth
def search():
    """
    renvoie une liste de tracks correspondant à la requête depuis divers services
    :return: un tableau contenant les infos que l'on a trouvé
    """
    query = request.form["q"]
    def parse_iso8601(x):
        t = x[2:-1].split("M")
        h=0
        if "H" in t[0]:
            h = int(t[0].split("H")[0])
            t[0]=t[0].split("H")[1]
        if len(t) == 2:
            return int(t[0])*60 + int(t[1])
        else:
            return int(t[0])
    results = []

    if "youtube" in CONFIG["search_providers"]:
        youtube_ids = None
        m = re.search("youtube.com/watch\?v=(\w+)", query)
        if m:
            youtube_ids = [m.groups()[0]]
        m = re.search("youtu.be/(\w+)", query)
        if m:
            youtube_ids = [m.groups()[0]]
        if youtube_ids:
            app.logger.info("Youtube video pasted by %s: %s", session["user"], youtube_ids[0])
        else:
            app.logger.info("Youtube search by %s : %s", session["user"], query)
            r = requests.get("https://www.googleapis.com/youtube/v3/search", params={
                "part":"snippet",
                "q":query,
                "key": CONFIG["youtube_key"],
                "type": "video"
            })
            if r.status_code != 200:
                raise Exception(r.text, r.reason)
            data = r.json()
            if len(data["items"]) == 0:   #   Si le servuer n'a rien trouvé
                raise Exception("nothing found on youtube")
            youtube_ids = [i["id"]["videoId"] for i in data["items"]]
        r = requests.get("https://www.googleapis.com/youtube/v3/videos", params={
            "part": "snippet,contentDetails",
            "key": CONFIG["youtube_key"],
            "id": ",".join(youtube_ids)
        })
        data = r.json()
        for i in data["items"]:
            results.append({
                "source": "youtube",
                "title": i["snippet"]["title"],
                "artist": i["snippet"]["channelTitle"],
                "url": "http://www.youtube.com/watch?v="+i["id"]    ,
                "albumart_url":  i["snippet"]["thumbnails"]["medium"]["url"],
                "duration": parse_iso8601(i["contentDetails"]["duration"])
            })
    return jsonify(results)

@app.route("/add", methods=['POST'])
@requires_auth
def add():
    """
    Ajoute l'url à la playlist
    """
    track = request.form.to_dict()
    print("adding", track)
    track["user"] = session["user"]
    with playlist_lock:
        playlist.append(track)
        conn = sqlite3.connect("jukebox.sqlite3")
        c = conn.cursor()
        c.execute("INSERT INTO log(track,user) VALUES (?,?)", (json.dumps(track), session['user']))
        conn.commit()
        if len(playlist) == 1:
            threading.Thread(target=player_worker).start()
    return "ok"
@app.route("/remove", methods=['POST'])
@requires_auth
def remove():
    """supprime la track de la playlist"""
    track = request.form
    with playlist_lock:
        print("removing", track)
        for i in playlist:
            if i["url"] == track["url"]:
                if playlist.index(i) == 0:
                    player_skip.set()
                else:
                    playlist.remove(i)
                break
        else:
            print("not found !")
    return "ok"
if __name__ == "__main__":
    app.run(host=CONFIG["listen_addr"], port=CONFIG["listen_port"], debug=CONFIG["debug"])
