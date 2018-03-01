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
from flask import Flask, render_template, session, request, redirect, jsonify
from config import CONFIG

maclist_lock = threading.Lock()
maclist = []
app = Flask(__name__)
app.secret_key = CONFIG["secret_key"]
conn = sqlite3.connect("jukebox.sqlite3")
playlist_lock = threading.Lock()
playlist = []
player_skip = threading.Event()

@app.route("/")
def accueil():
    """Renvoie la page d'accueil"""
    user = None
    c=conn.cursor()
    mac = mac_auth.get_mac(request.remote_addr)
    session["mac"] = mac
    if "user" not in session:
        session["user"] = None

    if session["mac"] is not None and session["user"] is None:
        c.execute("SELECT user FROM macs WHERE mac=?", (session["mac"],))
        r = c.fetchone()
        if r is not None:
            session["user"] = r[0]

    return render_template("accueil.html", user=session["user"], mac=session["mac"])

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

    global maclist, maclist_lock
    mac = session["mac"]
    now = time.time()
    timeout=120
    new_maclist = []
    found=False
    with maclist_lock:
        for m,t in maclist:
            if m == mac:
                found=True
                new_maclist.append((mac,now))
            elif t > now - timeout:
                new_maclist.append((m,t))
        if found==False:
            new_maclist.append((mac,now))
        maclist=new_maclist

    # récupération du temps écoulé
    elapsed = 0
    res = {
        "playlist": playlist,
        "time": elapsed, # temps actuel
        "maclist": maclist,
    }

    return jsonify(res)

@app.route("/auth", methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template("auth.html")
    success=False
    c = conn.cursor()
    if request.form["action"] == "S'enregistrer":
        c.execute('INSERT INTO users VALUES (?,?)',(
            request.form["user"],
            hashlib.sha512(request.form["pass"].encode()).hexdigest()
        ))
        conn.commit()
        success=True
    else:
        c = conn.cursor()
        c.execute("SELECT user FROM users WHERE user=? AND pass=?",(
            request.form["user"],
            hashlib.sha512(request.form["pass"].encode()).hexdigest()
        ))
        if c.fetchone() != None:
            success=True
    if success == True:
        session['user'] = request.form['user']
        c.execute("REPLACE INTO macs (user, mac) VALUES (?,?)",(
            request.form["user"],
            session["mac"]
        ))
        conn.commit()
    return redirect("/")
@app.route("/search/<query>", methods=['GET'])
def search(query):
    """
    renvoie une liste de tracks correspondant à la requête depuis divers services
    :return: un tableau contenant les infos que l'on a trouvé
    """
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

    # SPOTIFY
    if "spotify" in CONFIG["search_providers"]:
        r = requests.get("http://api.spotify.com/v1/search", params={
            "q": query,
            "type": "track",
            "market": "FR",
            "limit": 4
        }, headers={"Authorization": "Bearer "+libspotify.get_token()})
        if r.status_code != 200:
            raise Exception(r.status, r.reason)
        data = r.json()
        if len(data["tracks"]["items"]) == 0:   #   Si le servuer n'a rien trouvé
            raise Exception("nothing found on spotify")
        for i in data["tracks"]["items"]:   #   Sinon on lit les résultats
            results.append({
                "source": "spotify",
                "title": i["name"],
                "artist": i["artists"][0]["name"], # TODO: il peut y avoir plusieurs artistes
                "duration": int(i["duration_ms"])/1000,
                "url": i["uri"],
                "albumart_url": i["album"]["images"][2]["url"],
                "album": i["album"]["name"]
            })
	
	# YOUTUBE
    if "youtube" in CONFIG["search_providers"]:
        r = requests.get("https://www.googleapis.com/youtube/v3/search", params={
            "part":"snippet",
            "q":query,
            "key": CONFIG["youtube_key"],
            "type": "video"
        })
        if r.status_code != 200:
            raise Exception(r.text, r.reason)
        data = r.json()
        print(",".join([i["id"]["videoId"] for i in data["items"]]))
        if len(data["items"]) == 0:   #   Si le servuer n'a rien trouvé
            raise Exception("nothing found on youtube")  
        r = requests.get("https://www.googleapis.com/youtube/v3/videos", params={
            "part": "snippet,contentDetails",
            "key": CONFIG["youtube_key"],
            "id": ",".join([i["id"]["videoId"] for i in data["items"]])
        })
        data = r.json()
        for i in data["items"]:
            print(i)
            results.append({
                "source": "youtube",
                "title": i["snippet"]["title"],
                "artist": i["snippet"]["channelTitle"],
                "url": "http://www.youtube.com/watch?v="+i["id"]    ,
                "albumart_url":  i["snippet"]["thumbnails"]["medium"]["url"],
                "duration": parse_iso8601(i["contentDetails"]["duration"])
            })
    return jsonify(results)
@app.route("/logout")
def logout():
    session['user'] = None
    return redirect("/")
@app.route("/add", methods=['POST'])
def add():
    """
    Ajoute l'url à la playlist
    """
    track = request.form
    print("adding", track)
    with playlist_lock:
        playlist.append(track)
        if len(playlist) == 1:
            threading.Thread(target=player_worker).start()
    return "ok"
@app.route("/remove", methods=['POST'])
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
    app.run(host=CONFIG["listen_addr"], port=CONFIG["listen_port"])
