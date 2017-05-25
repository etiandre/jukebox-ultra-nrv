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
    """
    Renvoie quelque choise du type:
    {
   "time":0,
   "playlist":[
      {
         "album":"Fusa",
         "artist":"Macromism",
         "url":"spotify:track:2L4GpAeRotv9jKIMas6lXv",
         "albumart_url":"https://i.scdn.co/image/eef87e5ce12499aa221578056a57e1a82b025609",
         "track":"Untoldyou",
         "duration":"430"
      }
   ]
}
    """
    client = MPDClient()
    client.connect("localhost", 6600)
    status = client.status()
    playlist = client.playlistinfo()
    client.close()
    client.disconnect()

    play = []
    for i in range(len(playlist)):
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
        "playlist": play,
        "time": elapsed # temps actuel
    }

    return json.dumps(res)

@app.route("/add/<url>")
def add(url):
    """
    Adds an url to the request playlist
    """
    client = MPDClient()
    client.connect("localhost", 6600)
    client.add(url)
    if len(client.playlistinfo()) == 1:
        client.play()
    client.close()
    client.disconnect()
    return "ok"
if __name__ == "__main__":
    client = MPDClient()
    client.connect("localhost", 6600)
    # client.clear() # on vide la liste de requêtes lors du lancement
    client.random(0) # lecture séquentielle
    client.consume(1) # activation de l'option qui mange les pistes au fur et à mesure de la lecture
    client.close()
    client.disconnect()
    search.app.run(host='0.0.0.0', port=8080)
