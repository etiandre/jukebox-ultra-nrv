from flask import Blueprint, render_template, redirect, session, jsonify, request
from flask import current_app as app
from jukebox.src.util import *
import subprocess, requests

main=Blueprint('main', __name__)
@main.route("/app")
@requires_auth
def app_view():
    app.logger.info("App access from %s %s", session["user"], session["mac"])
    return render_template("accueil.html", user=session["user"], mac=session["mac"])


@main.route("/")
def accueil():
    return redirect("/app")
 
@main.route("/sync")
def sync():
    """
    Renvoie quelque choise du type vnr
    """
    # récupération du temps écoulé
    amixer_out = subprocess.check_output(['amixer', 'get', "'Master',0"]).decode()
    volume = re.findall("Playback \d+ \[(\d+)%\]",amixer_out)[0]
    res = {
        "playlist": app.playlist,
        "volume": volume,
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
    def parse_iso8601(x):
        t = x[2:-1].split("M")
        h=0
        if "H" in t[0]:
            h = int(t[0].split("H")[0])
            t[0]=t[0].split("H")[1]
        if len(t) == 2:
            return int(t[0])*60 + int(t[1])
        else:
            return int(t[0])
    results = []

    youtube_ids = None
    m = re.search("youtube.com/watch\?v=(\w+)", query)
    if m:
        youtube_ids = [m.groups()[0]]
    m = re.search("youtu.be/(\w+)", query)
    if m:
        youtube_ids = [m.groups()[0]]
    if youtube_ids:
        app.logger.info("Youtube video pasted by %s: %s", session["user"], youtube_ids[0])
    else:
        app.logger.info("Youtube search by %s : %s", session["user"], query)
        r = requests.get("https://www.googleapis.com/youtube/v3/search", params={
            "part":"snippet",
            "q":query,
            "key": app.config["YOUTUBE_KEY"],
            "type": "video"
        })
        if r.status_code != 200:
            raise Exception(r.text, r.reason)
        data = r.json()
        if len(data["items"]) == 0:   #   Si le servuer n'a rien trouvé
            raise Exception("nothing found on youtube")
        youtube_ids = [i["id"]["videoId"] for i in data["items"]]
    r = requests.get("https://www.googleapis.com/youtube/v3/videos", params={
        "part": "snippet,contentDetails",
        "key": app.config["YOUTUBE_KEY"],
        "id": ",".join(youtube_ids)
    })
    data = r.json()
    for i in data["items"]:
        results.append({
            "source": "youtube",
            "title": i["snippet"]["title"],
            "artist": i["snippet"]["channelTitle"],
            "url": "http://www.youtube.com/watch?v="+i["id"]    ,
            "albumart_url":  i["snippet"]["thumbnails"]["medium"]["url"],
            "duration": parse_iso8601(i["contentDetails"]["duration"])
        })
    return jsonify(results)
