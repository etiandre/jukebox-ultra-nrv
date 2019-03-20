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
    results.append({
        "source": "soundcloud",
        "title": "Unknown",
        "artist": "Unknown",
        "url": query,
        "albumart_url": None,
        "duration": None,
        "id": None
        })
    return results
