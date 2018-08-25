from flask import Blueprint, render_template, redirect, session, jsonify, request
from flask import current_app as app
from jukebox.src.util import *
import subprocess, requests, importlib

main = Blueprint('main', __name__)


@main.route("/app")
@requires_auth
def app_view():
    app.logger.info("App access from %s", session["user"])
    return render_template(
        "accueil.html", user=session["user"])


@main.route("/")
def accueil():
    return redirect("/app")


@main.route("/sync")
def sync():
    """
    Renvoie quelque choise du type vnr
    """
    amixer_out = subprocess.check_output(['amixer', 'get',
                                          "'Master',0"]).decode()
    volume = re.findall("Playback \d+ \[(\d+)%\]", amixer_out)[0]
    res = {
        "playlist": app.playlist,
        "volume": volume,
        "time": app.player_time
    }

    return jsonify(res)


@main.route("/search", methods=['POST'])
@requires_auth
def search():
    """
    renvoie une liste de tracks correspondant à la requête depuis divers services
    :return: un tableau contenant les infos que l'on a trouvé
    """
    query = request.form["q"]
    results = []
    for i in app.search_backends:
        results += i.search(query)
    return jsonify(results)
