"""Ce module présente les fonctions administrateur"""

from jukebox import app

@app.route("/admin/play")
def play():
    """Force la lecture"""
    pass

@app.route("/admin/set-volume", methods=["POST"])
def set_volume():
    """Fixe le volume de sortie"""
    pass

@app.route("/admin/stop")
def stop():
    """Stoppe la lecture"""
    pass

@app.route("/admin/play-playlist/<id>")
def play_playlist(id):
    """Force la lecture de telle playlist"""
    pass