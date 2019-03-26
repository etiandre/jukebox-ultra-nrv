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
    results.append({
        "source": "bandcamp",
        "title": json_info["track"],
        "artist": json_info["artist"],
        "url": query,
        "albumart_url": json_info["thumbnail"],
        "duration": int(json_info["duration"]),
        "id": json_info["id"]
        })
    return results
