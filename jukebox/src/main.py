import re
import datetime
import sys
from flask import Blueprint, render_template, redirect, session, jsonify, request, flash
from flask import current_app as app
from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from os import listdir
from os.path import isfile, join

from jukebox.src.util import *
from jukebox.src.Track import Track
from jukebox.src.statistics import create_html_users, create_html_tracks

main = Blueprint('main', __name__)


def get_style():
    try:
        if session["stylesheet"] is not None:
            stylesheet = session["stylesheet"]
        else:
            stylesheet = app.stylesheet
    except KeyError:
        stylesheet = app.stylesheet
    return stylesheet


def get_nav_links():
    if "NAV_LINKS" in app.config:
        return app.config["NAV_LINKS"]
    else:
        return []


@main.route("/app")
@requires_auth
def app_view():
    # app.logger.info("App access from %s", session["user"])
    return render_template("accueil.html",
                           user=session["user"], jk_name=app.config["JK_NAME"],
                           stylesheet=get_style(), navlinks=get_nav_links())


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
    return render_template("help.html", modules=modules,
                           jk_name=app.config["JK_NAME"],
                           stylesheet=get_style(), navlinks=get_nav_links(),
                           version=app.version)


@main.route("/settings", methods=['GET', 'POST'])
def settings():
    # we should add a modules argument to render_template to
    # display which search functions are available

    style_path = "jukebox/static/styles/custom/"
    styles = [(f, f) for f in listdir(style_path) if isfile(join(style_path, f)) and f[-4:] == ".css"]
    app.logger.info(styles)

    class SettingsForm(FlaskForm):
        style = SelectField("Styles", choices=styles)
        submit = SubmitField("Send")
    form = SettingsForm()

    if request.method == 'POST':
        # if not(form.validate()):
        #    flash('All fields are required.')
        #    app.logger.info("All fields are required.")
        #    return render_template('settings.html',
        #            jk_name = app.config["JK_NAME"],form = form)
        # else:
        # app.logger.info(request.form)
        style = request.form["style"]
        session["stylesheet"] = style
        # app.logger.info("Style : " + style)
        return render_template('settings.html', user=session["user"],
                               jk_name=app.config["JK_NAME"], form=form,
                               stylesheet=get_style(), navlinks=get_nav_links())
    elif request.method == 'GET':
        return render_template('settings.html', user=session["user"],
                               jk_name=app.config["JK_NAME"], form=form,
                               stylesheet=get_style(), navlinks=get_nav_links())


@main.route("/sync")
def sync():
    """
    Renvoie la playlist en cours
    """
    volume = 0
    time_pos = 0
    # segfault was here
    with app.mpv_lock:
        if hasattr(app, 'mpv') and app.mpv is not None:
            volume = app.mpv.volume
            if hasattr(app.mpv, 'time_pos') and app.mpv.time_pos is not None:
                time_pos = app.mpv.time_pos  # when track is finished, continues augmenting time_pos
    
    res = {
        "playlist": app.playlist,
        "volume": volume,
        "time": time_pos
    }

    return jsonify(res)


@main.route("/move-track", methods=['POST'])
@requires_auth
def move_track():
    try:
        action = request.form["action"]
        randomid = request.form["randomid"]
    except KeyError:
        return "nok"

    index = None
    with app.playlist_lock:
        for x in app.playlist:
            if str(x["randomid"]) == randomid:
                index = app.playlist.index(x)
                break
        if index is None:
            # app.logger.warning("Track {} not found".format(randomid))
            return "nok"
        if action == "up":
            if index < 2:
                app.logger.warning("Track {} has index".format(index))
                return "nok"
            track_temp = app.playlist[index-1]
            app.playlist[index-1] = app.playlist[index]
            app.playlist[index] = track_temp
        elif action == "down":
            if len(app.playlist)-2 < index or index < 1:
                # app.logger.warning("Track {} has index".format(index))
                return "nok"
            track_temp = app.playlist[index+1]
            app.playlist[index+1] = app.playlist[index]
            app.playlist[index] = track_temp
        else:
            return "nok"
    return "ok"


@main.route("/statistics", methods=['GET'])
@requires_auth
def statistics():
    return render_template('statistics.html', user=session["user"],
                           jk_name=app.config["JK_NAME"],
                           table_users_count_all=create_html_users(app.config["DATABASE_PATH"], nbr=-1),
                           table_users_count_week=create_html_users(app.config["DATABASE_PATH"], nbr=10,
                                                                    date=datetime.datetime.now()
                                                                        - datetime.timedelta(weeks=1)),
                           table_users_count_day=create_html_users(app.config["DATABASE_PATH"], nbr=10,
                                                                   date=datetime.datetime.now()
                                                                        - datetime.timedelta(days=1)),
                           table_tracks_count_all=create_html_tracks(app.config["DATABASE_PATH"], nbr=20),
                           table_tracks_count_week=create_html_tracks(app.config["DATABASE_PATH"], nbr=10,
                                                                      date=datetime.datetime.now()
                                                                           - datetime.timedelta(weeks=1)),
                           table_tracks_count_day=create_html_tracks(app.config["DATABASE_PATH"], nbr=10,
                                                                     date=datetime.datetime.now()
                                                                          - datetime.timedelta(days=1)),

                           stylesheet=get_style(), navlinks=get_nav_links())


@main.route("/status", methods=['GET'])
def status():
    res = {
        "status": "UP"
    }
    return jsonify(res)


@main.route("/refresh-track", methods=['POST'])
@requires_auth
def refresh_track():
    """
    For now the interface isn't refreshed
    :return:
    """
    try:
        url = request.form["url"]
    except KeyError:
        return "nok"
    with app.database_lock:
        Track.refresh_by_url(app.config["DATABASE_PATH"], url)
    return "ok"


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
    regex_soundcloud = re.compile('^(http://|https://)?(www.)?soundcloud.com')
    regex_twitch = re.compile('^(http://|https://)?(www.)?twitch.tv')
    regex_jamendo = re.compile('^(https?://)?(www.)?jamendo.com')
    regex_search_soundcloud = re.compile('(\!sc\s)|(.*\s\!sc\s)|(.*\s\!sc$)')
    regex_search_youtube = re.compile('(\!yt\s)|(.*\s\!yt\s)|(.*\s\!yt$)')
    regex_generic = re.compile('(\!url\s)|(.*\s\!url\s)|(.*\s\!url$)|(\!g\s)|(.*\s\!g\s)|(.*\s\!g$)')

    # print("Query : \"" + query + "\"")
    # print("Regex match :", re.match(regex_generic, query))
    # print('jukebox.src.backends.search.jamendo' in sys.modules)
    # Bandcamp
    if re.match(regex_bandcamp, query) is not None \
    and 'jukebox.src.backends.search.bandcamp' in sys.modules:
        for bandcamp in app.search_backends:
            if bandcamp.__name__ == 'jukebox.src.backends.search.bandcamp':
                break
        results += bandcamp.search_engine(query)
    # Soundcloud
    elif re.match(regex_soundcloud, query) is not None \
    and 'jukebox.src.backends.search.soundcloud' in sys.modules:
        for soundcloud in app.search_backends:
            if soundcloud.__name__ == 'jukebox.src.backends.search.soundcloud':
                break
        results += soundcloud.search_engine(query)
    elif re.match(regex_jamendo, query) is not None \
    and 'jukebox.src.backends.search.jamendo' in sys.modules:
        for jamendo in app.search_backends:
            if jamendo.__name__ == 'jukebox.src.backends.search.jamendo':
                break
        results += jamendo.search_engine(query)
    # Soundcloud search
    elif re.match(regex_search_soundcloud, query) is not None \
    and 'jukebox.src.backends.search.soundcloud' in sys.modules:
        for soundcloud in app.search_backends:
            if soundcloud.__name__ == 'jukebox.src.backends.search.soundcloud':
                break
        results += soundcloud.search_multiples(re.sub("\!sc", "", query))
    # Twitch
    if re.match(regex_twitch, query) is not None \
    and 'jukebox.src.backends.search.twitch' in sys.modules:
        for twitch in app.search_backends:
            if twitch.__name__ == 'jukebox.src.backends.search.twitch':
                break
        results += twitch.search_engine(query)

    # Youtube search (explicit)
    elif re.match(regex_search_youtube, query) is not None \
    and 'jukebox.src.backends.search.youtube' in sys.modules:
        for youtube in app.search_backends:
            if youtube.__name__ == 'jukebox.src.backends.search.youtube':
                break
        results += youtube.search_engine(re.sub("\!yt", "", query), use_youtube_dl=True)

    # Generic extractor
    elif re.match(regex_generic, query) is not None \
    and 'jukebox.src.backends.search.generic' in sys.modules:
        for generic in app.search_backends:
            if generic.__name__ == 'jukebox.src.backends.search.generic':
                break
        results += generic.search_engine(re.sub("\!url", "", query))

    elif 'jukebox.src.backends.search.youtube' in sys.modules:
        for youtube in app.search_backends:
            if youtube.__name__ == 'jukebox.src.backends.search.youtube':
                break
        results += youtube.search_engine(query)
    else:
        app.logger.error("Error: no search module found")
    return jsonify(results)
