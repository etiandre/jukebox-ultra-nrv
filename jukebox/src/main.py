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
    #app.logger.info("App access from %s", session["user"])
    return render_template("accueil.html",
            user=session["user"], jk_name = app.config["JK_NAME"])


@main.route("/")
def accueil():
    return redirect("/app")

@main.route("/help")
def help():
    # we should add a modules argument to render_template to
    # display which search functions are available
    modules = []
    for i in app.config["SEARCH_BACKENDS"]:
        modules.append(i)
    #print(modules)
    return render_template("help.html", modules = modules,
            jk_name = app.config["JK_NAME"])


@main.route("/sync")
def sync():
    """
    Renvoie quelque choise du type vnr
    """
    amixer_out = subprocess.check_output(['amixer', 'get',
                                          "'Master',0"]).decode()
    volume = re.findall("Playback \d+ \[(\d+)%\]", amixer_out)[0]
    if hasattr(app, 'mpv') and app.mpv is not None:
        #app.logger.info("MPV exists")
        time_pos = app.mpv.time_pos
    else:
        #app.logger.info("Second except")
        time_pos = 0
    res = {
        "playlist": app.playlist,
        "volume": volume,
        "time": time_pos
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
    regex_bandcamp = re.compile('^(http://|https://)?\S*\.bandcamp.com')
    regex_soundcloud = re.compile('^(http://|https://)?soundcloud.com')
    regex_jamendo = re.compile('^(https?://)?(www.)?jamendo.com')
    regex_search_soundcloud = re.compile('(\!sc\s)|(.*\s\!sc\s)|(.*\s\!sc$)')
    regex_search_youtube = re.compile('(\!yt\s)|(.*\s\!yt\s)|(.*\s\!yt$)')
    regex_generic = re.compile('(\!url\s)|(.*\s\!url\s)|(.*\s\!url$)')


    #print("Query : \"" + query + "\"")
    #print("Regex match :", re.match(regex_generic, query))
    #print('jukebox.src.backends.search.jamendo' in sys.modules)
    # Bandcamp
    if re.match(regex_bandcamp, query) != None \
    and 'jukebox.src.backends.search.bandcamp' in sys.modules:
        for bandcamp in app.search_backends:
            if bandcamp.__name__ == 'jukebox.src.backends.search.bandcamp':
                break
        results += bandcamp.search(query)
    # Soundcloud
    elif re.match(regex_soundcloud, query) != None \
    and 'jukebox.src.backends.search.soundcloud' in sys.modules:
        for soundcloud in app.search_backends:
            if soundcloud.__name__ == 'jukebox.src.backends.search.soundcloud':
                break
        results += soundcloud.search(query)
    elif re.match(regex_jamendo, query) != None \
    and 'jukebox.src.backends.search.jamendo' in sys.modules:
        for jamendo in app.search_backends:
            if jamendo.__name__ == 'jukebox.src.backends.search.jamendo':
                break
        results += jamendo.search(query)
    # Soundcloud search
    elif re.match(regex_search_soundcloud, query) != None \
    and 'jukebox.src.backends.search.soundcloud' in sys.modules:
        for soundcloud in app.search_backends:
            if soundcloud.__name__ == 'jukebox.src.backends.search.soundcloud':
                break
        results += soundcloud.search_engine(re.sub("\!sc", "", query))

    # Youtube search (explicit)
    elif re.match(regex_search_youtube, query) != None \
    and 'jukebox.src.backends.search.youtube' in sys.modules:
        for youtube in app.search_backends:
            if youtube.__name__ == 'jukebox.src.backends.search.youtube':
                break
        results += youtube.search_engine(re.sub("\!yt", "", query))

    # Generic extractor
    elif re.match(regex_generic, query) != None \
    and 'jukebox.src.backends.search.generic' in sys.modules:
        for generic in app.search_backends:
            if generic.__name__ == 'jukebox.src.backends.search.generic':
                break
        results += generic.search(re.sub("\!url", "", query))

    elif 'jukebox.src.backends.search.youtube' in sys.modules:
        for youtube in app.search_backends:
            if youtube.__name__ == 'jukebox.src.backends.search.youtube':
                break
        results += youtube.search(query)
    else:
        app.logger.error("Error: no search module found")
    return jsonify(results)
