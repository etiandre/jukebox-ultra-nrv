"""Ce module s'occupe de faire la correspondance entre un nom de track et une track"""

from jukebox import app
#from config import CONFIG
import http.client
import json
from urllib.parse import quote_plus

@app.route("/search/<query>", methods=['GET'])
def search(query):
    """renvoie une liste de tracks correspondant à la requête depuis divers services"""

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
        results.append({
            "track": i["name"],
            "artist": i["artists"][0]["name"], # TODO: il peut y avoir plusieurs artistes
            "duration": int(i["duration_ms"])/1000,
            "url": i["uri"],
            "albumart_url": i["album"]["images"][0]["url"] # TODO: prendre l'image la plus grande
        })
    return str(results) # TODO: faire la template
