# -*- coding: utf-8 -*-
import os
from mpd import MPDClient
import json
import libspotify
import requests

from flask import Flask, render_template
app = Flask(__name__)

# chargement du module de recherche
import search


@app.route("/")
def accueil():
    """Renvoie la page d'accueil"""
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
    # récupération de la playlist et de l'état de mopidy
    client = MPDClient()
    client.connect("localhost", 6600)
    status = client.status()
    playlist = client.playlistinfo()
    client.close()
    client.disconnect()

    play = []
    for i in range(len(playlist)):
        # récupération de l'album art
        play.append({
            "url": playlist[i]["file"],
            "duration": playlist[i]["time"],
            "artist": playlist[i]["artist"],
            "album": playlist[i]["album"],
            "track": playlist[i]["title"],
            "albumart_url": "static/albumart/" + playlist[i]["file"].split(":")[2]
        })

    # récupération du temps écoulé
    if "elapsed" in status:
        elapsed = int(status["elapsed"].split(".")[0])
    else:
        elapsed = -1
    res = {
        "playlist": play,
        "time": elapsed # temps actuel
    }

    return json.dumps(res)

@app.route("/add/<url>")
def add(url):
    """
    Ajoute l'url à la playlist
    """
    # récupération de l'album art
    r = requests.get("https://api.spotify.com/v1/tracks/"+url.split(":")[2],
                     headers={"Authorization": "Bearer " + libspotify.get_token()})
    if r.status_code != 200:
        raise Exception(r.status_code, r.reason)
    data = r.json()

    # téléchargement (caching) de l'album art
    os.system("wget "+data["album"]["images"][0]["url"]+" -O static/albumart/" + url.split(":")[2])

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
