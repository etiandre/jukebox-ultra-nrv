import sqlite3

from jukebox.src.util import *


class Track:
    def __init__(self, id, url, track, artist, source, albumart_url, album=None, duration=None, blacklisted=False):
        self.id = id
        self.url = url
        self.track = track
        self.artist = artist
        self.source = source
        self.albumart_url = albumart_url
        self.album = album
        self.duration = duration
        self.blacklisted = blacklisted

    def __str__(self):
        return self.id + ": " + self.url

    @classmethod
    def import_from_url(cls, database, url):
        conn = sqlite3.connect(database)
        c = conn.cursor()
        c.execute("""select *
                     from track_info
                     where url = ?;
                  """,
                  (url,))
        r = c.fetchall()
        print(r[0])
        return Track(id=r[0][0], url=r[0][1], track=r[0][2], artist=r[0][3], album=r[0][4], duration=r[0][5],
                     albumart_url=r[0][6], source=r[0][7], blacklisted=r[0][8])
