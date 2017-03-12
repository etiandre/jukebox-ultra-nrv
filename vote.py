"""Ce module permet de voter sur les playlists à jouer"""
from jukebox import app

@app.route("/vote", methods=["POST"])
def vote():
    """Vote pour la playlist"""