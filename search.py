"""Ce module s'occupe de faire la correspondance entre un nom de track et une track"""

from jukebox import app

@app.route("/search/<query>")
def search(query):
    """renvoie une liste de tracks correspondant à la requête depuis divers services"""
    pass