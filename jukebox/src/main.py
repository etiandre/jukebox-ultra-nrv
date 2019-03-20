import re
import sys
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
    # if query is http or https or nothing xxxxxxx.bandcamp.com/
    # then results += apps.search_backends.bandcamp(query)
    # (if bandcamp loaded)
    # similar for soundcloud
    # else we search only on youtube (in the future, maybe soundcloud too
    regex_bandcamp = re.compile('(http://|https://)?\S*\.bandcamp.com')
    regex_soundcloud = re.compile('(http://|https://)?soundcloud.com')

    #print(re.match(regex_soundcloud, query))
    #print('jukebox.src.backends.search.soundcloud' in sys.modules)
    if re.match(regex_bandcamp, query) != None \
    and 'jukebox.src.backends.search.bandcamp' in sys.modules:
        for bandcamp in app.search_backends:
            if bandcamp.__name__ == 'jukebox.src.backends.search.bandcamp':
                break
        results += bandcamp.search(query)
    elif re.match(regex_soundcloud, query) != None \
    and 'jukebox.src.backends.search.soundcloud' in sys.modules:
        for soundcloud in app.search_backends:
            if soundcloud.__name__ == 'jukebox.src.backends.search.soundcloud':
                break
        results += soundcloud.search(query)
    elif 'jukebox.src.backends.search.youtube' in sys.modules:
        for youtube in app.search_backends:
            if youtube.__name__ == 'jukebox.src.backends.search.youtube':
                break
        results += youtube.search(query)
    else:
        print("Error: no search module found")
    return jsonify(results)
