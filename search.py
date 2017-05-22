"""Ce module s'occupe de faire la correspondance entre un nom de track et une track"""

from jukebox import app
#from config import CONFIG
import http.client
import json
from urllib.parse import quote_plus
from flask import request

@app.route("/search", methods=['GET'])
def search(query):
    """
    renvoie une liste de tracks correspondant à la requête depuis divers services
    :return: un tableau contenant les infos que l'on a trouvé
    """

    query = request.form["q"];


    results = []

    #   demande à Spotify la musique que l'on cherche
    #   WARNING: le serveur répond sous forme de JSON
    conn = http.client.HTTPSConnection("api.spotify.com")
    conn.request("GET", "/v1/search?q="+quote_plus(query)+"&type=track&market=FR&limit=10")
    r = conn.getresponse()

    #   Si le serveur nous dit qu'il n'y a pas d'erreur
    if r.status != 200:
        raise Exception(r.status, r.reason)

    data = json.load(r)
    if len(data["tracks"]["items"]) == 0:   #   Si le servuer n'a rien trouvé
        raise Exception("nothing found on spotify")
    for i in data["tracks"]["items"]:   #   Sinon on lit les résultats

        #   Cette partie sert a déterminer la plus grande image
        taillemax = 0
        indextaillemax = 0
        for index in range(i["album"]["images"]):   #   On regarde le nombre de pixel
            if i["album"]["images"][index]["height"] * i["album"]["images"][index]["width"] > taillemax:
                taillemax = i["album"]["images"][index]["height"] * i["album"]["images"][index]["width"]
                indextaillemax = index

        results.append({
            "track": i["name"],
            "artist": i["artists"][0]["name"], # TODO: il peut y avoir plusieurs artistes
            "duration": int(i["duration_ms"])/1000,
            "url": i["uri"],
            "albumart_url": i["album"]["images"][indextaillemax]["url"] # TODO: prendre l'image la plus grande
                                                                        #  Normalement c'est bon
        })
    return json.dumps(results)
