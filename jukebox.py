# -*- coding: utf-8 -*-
import os,sys
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
app = Flask(__name__)

#import playpause
import search
#import admin
#import vote
#import playlist
from mpd import MPDClient
import json
if sys.version_info[0] == 3:
    import http.client as httplib
    from urllib.parse import quote_plus
else:
    import httplib
    from urllib import quote_plus

@app.route("/")
def accueil():
    return render_template("accueil.html")

@app.route("/sync")
def sync():
    client = MPDClient()
    client.connect("localhost", 6600)
    status = client.status()
    playlist = client.playlistinfo()
    client.close()
    client.disconnect()

    play = []
    for i in range(len(playlist)):
        if i <= int(status["nextsong"]):
            continue # on ignore les pistes déjà lues
        # récupération de l'album art
        conn = httplib.HTTPSConnection("api.spotify.com")
        conn.request("GET", "/v1/albums/" + playlist[i]["x-albumuri"].split(":")[2])
        r = conn.getresponse()
        if r.status != 200:
            raise Exception(r.status, r.reason)
        data = json.load(r)
        play.append({
            "url": playlist[i]["file"],
            "duration": playlist[i]["time"],
            "artist": playlist[i]["artist"],
            "album": playlist[i]["album"],
            "track": playlist[i]["title"],
            "albumart_url": data["images"][0]["url"]
        })

    # récupération du temps écoulé
    if "elapsed" in status:
        elapsed = int(status["elapsed"].split(".")[0])
    else:
        elapsed = 0
    res = {
        "next": play,
        "time": elapsed # temps actuel
    }

    return json.dumps(res)

if __name__ == "__main__":
    search.app.run(host='0.0.0.0', port=8080)
