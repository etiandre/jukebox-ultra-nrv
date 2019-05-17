import html
import re
import json
import youtube_dl
from html.parser import HTMLParser
from flask import current_app as app
from flask import session

ydl_opts = {
        'skip_download': True,
        }

def search(query):
    """
    Search for a bandcamp url
    """
    results = []
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        json_info = ydl.extract_info(query, False)
    print(json.dumps(json_info))

    # If we have a playlist
    if "_type" in json_info and json_info["_type"] == "playlist":
        for res in json_info["entries"]:
            results.append({
                "source": "bandcamp",
                "title": res["track"],
                "artist": res["artist"],
                "album": res["album"],
                "url": res["webpage_url"],
                "albumart_url": res["thumbnails"][0]["url"],
                "duration": int(res["duration"]),
                "id": res["id"]
                })

    # It's a single music
    else:
        results.append({
            "source": "bandcamp",
            "title": json_info["track"],
            "artist": json_info["artist"],
            "album": json_info["album"],
            "url": query,
            "albumart_url": json_info["thumbnail"],
            "duration": int(json_info["duration"]),
            "id": json_info["id"]
            })
    return results
