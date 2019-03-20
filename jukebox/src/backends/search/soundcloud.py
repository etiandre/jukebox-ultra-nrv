import re, requests
from flask import current_app as app
from flask import session

import youtube_dl
import json

def search(query):
    results = []

    # We use youtube-dl to get the song metadata
    # only problem : it's a bit slow (about 3 seconds)
    ydl_opts = {
            'writeinfojson': True,
            'skip_download': True, # we do want only a json file
            'outtmpl': "tmp_music", # the json is tmp_music.info.json
            }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([query])

    with open("tmp_music.info.json", 'r') as f:
        metadata = f.read()
        metadata = json.loads(metadata)
        print(type(metadata))


    results.append({
        "source": "soundcloud",
        "title": metadata["title"],
        "artist": metadata["uploader"],
        "url": query,
        "albumart_url": metadata["thumbnail"],
        "duration": metadata["duration"],
        "id": metadata["id"]
        })
    return results
