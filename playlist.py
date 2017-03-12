"""
Ce module s'occupe de gérer les playlists et l'édition de celles-ci
"""
from jukebox import app

@app.route("/playlist/list")
def list():
    """renvoie la liste des playlists disponibles"""
    pass

@app.route("/playlist/<id>")
def show_playlist(id):
    """renvoie le contenu de la playlist correspondant à id"""
    pass

@app.route("/playlist/<id>/add", methods=["POST"])
def add_track_to_playlist(id):
    """ajoute la track dans la playlist"""
    pass

@app.route("/playlist/<id>/remove", methods=["POST"])
def remove_track_from_playlist(id):
    """supprime la track depuis la playlist"""
    pass

@app.route("/playlist/<id>/move", methods=["POST"])
def move_track(id):
    """échange deux tracks dans une playlists (change l'ordre)"""
    pass