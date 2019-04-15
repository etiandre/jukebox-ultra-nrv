import re, requests
from flask import current_app as app
from flask import session
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
    if youtube_ids:
        app.logger.info("Youtube video pasted by %s: %s", session["user"],
                        youtube_ids[0])
    else:
        app.logger.info("Youtube search by %s : %s", session["user"], query)
        r = requests.get(
            "https://www.googleapis.com/youtube/v3/search",
            params={
                "part": "snippet",
                "q": query,
                "key": app.config["YOUTUBE_KEY"],
                "type": "video"
            })
        if r.status_code != 200:
            raise Exception(r.text, r.reason)
        data = r.json()
        if len(data["items"]) == 0:  #   Si le servuer n'a rien trouvé
            raise Exception("nothing found on youtube")
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
