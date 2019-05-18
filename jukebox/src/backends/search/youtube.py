import re, requests
from flask import current_app as app
from flask import session
import youtube_dl
import json
# Parse YouTube's length format
# TODO: Completely buggy.


def parse_iso8601(x):
    t = [int(i) for i in re.findall("(\d+)", x)]
    r = 0
    for i in range(len(t)):
        r += 60**(i) * t[-i-1]
    return r


def search(query):
    results = []
    youtube_ids = None
    m = re.search("youtube.com/watch\?v=([\w\d\-_]+)", query)
    if m:
        youtube_ids = [m.groups()[0]]
    m = re.search("youtu.be/(\w+)", query)
    if m:
        youtube_ids = [m.groups()[0]]
    #if youtube_ids:
        #app.logger.info("Youtube video pasted by %s: %s", session["user"], youtube_ids[0])
    #else:
        #app.logger.info("Youtube search by %s : %s", session["user"], query)
    r = requests.get(
        "https://www.googleapis.com/youtube/v3/search",
        params={
            "part": "snippet",
            "q": query,
            "key": app.config["YOUTUBE_KEY"],
            "type": "video"
        })
    if r.status_code != 200:
        if r.status_code != 403:
            raise Exception(r.text, r.reason)
        else:
            return search_fallback(query)
    data = r.json()
    if len(data["items"]) == 0:  #   Si le serveur n'a rien trouvé
        app.logger.warning("Nothing found on youtube for query {}".format(query))
    youtube_ids = [i["id"]["videoId"] for i in data["items"]]
    r = requests.get(
        "https://www.googleapis.com/youtube/v3/videos",
        params={
            "part": "snippet,contentDetails",
            "key": app.config["YOUTUBE_KEY"],
            "id": ",".join(youtube_ids)
        })
    data = r.json()
    for i in data["items"]:
        album = None
        results.append({
            "source": "youtube",
            "title": i["snippet"]["title"],
            "artist": i["snippet"]["channelTitle"],
            "url": "http://www.youtube.com/watch?v=" + i["id"],
            "albumart_url": i["snippet"]["thumbnails"]["medium"]["url"],
            "duration": parse_iso8601(i["contentDetails"]["duration"]),
            "id": i["id"],
            "album": album,
        })
    return results


def search_engine(query):
    return search(query)


def search_fallback(query):
    ydl_opts = {
        'writeinfojson': True,
        'skip_download': True,  # we do want only a json file
        'outtmpl': "tmp_music_%(playlist_index)s",  # the json is tmp_music.info.json
        }

    results = []

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download(["ytsearch5:" + query])
            # TODO : for now, we just interrupt the search, it could
            # be cool to have a yt-dl option to ignore it
        except youtube_dl.utils.DownloadError:
            pass

    for i in range(5):

        with open("tmp_music_" + str(i+1) + ".info.json", 'r') as f:
            metadata = f.read()
            metadata = json.loads(metadata)
            # app.logger.info(metadata)

        """
        app.logger.info("Title: {}".format(metadata["title"]))
        app.logger.info("Track: {}".format(metadata["track"]))
        app.logger.info("Alt Title: {}".format(metadata["alt_title"]))
        app.logger.info("Album: {}".format(metadata["album"]))
        app.logger.info("Artist: {}".format(metadata["artist"]))
        app.logger.info("Uploader: {}".format(metadata["uploader"]))
        """

        title = metadata["title"]
        if title is None and metadata["track"] is not None:
            title = metadata["track"]
        artist = metadata["artist"]
        if artist is None:
            artist = metadata["uploader"]
        album = metadata["album"]

        results.append({
            "source": "youtube",
            "title": title,
            "artist": artist,
            "album": album,
            "url": metadata["webpage_url"],
            "albumart_url": metadata["thumbnail"],
            "duration": metadata["duration"],
            "id": metadata["id"]
            })
    return results
