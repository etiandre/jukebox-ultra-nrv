import sqlite3

from jukebox.src.util import *


class Track:
    def __init__(self, ident, url, track, artist, source, albumart_url, album=None, duration=None, blacklisted=False,
                 user=None):
        """

        :param id:
        :param url:
        :param track:
        :param artist:
        :param source:
        :param albumart_url:
        :param album:
        :param duration:
        :param blacklisted:
        :param user: may be None, else it means we get it from a log
        """
        self.ident = ident
        self.url = url
        self.track = track
        self.artist = artist
        self.source = source
        self.albumart_url = albumart_url
        self.album = album
        self.duration = duration
        self.blacklisted = blacklisted
        self.user = user

    def __str__(self):
        return self.ident + ": " + self.url

    @classmethod
    def import_from_id(cls, database, ident):
        """

        :param database:
        :param ident:
        :return:
        """
        conn = sqlite3.connect(database)
        c = conn.cursor()
        c.execute("SELECT * FROM track_info WHERE id = ?;", (ident,))
        r = c.fetchone()
        if r is None:
            return None
        assert r[0] == ident
        return Track(ident=r[0], url=r[1], track=r[2], artist=r[3], album=r[4], duration=r[5], albumart_url=r[6],
                     source=r[7], blacklisted=r[8])

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
        if r is None:
            return None
        return Track(ident=r[0][0], url=r[0][1], track=r[0][2], artist=r[0][3], album=r[0][4], duration=r[0][5],
                     albumart_url=r[0][6], source=r[0][7], blacklisted=r[0][8])

    @classmethod
    def get_random_track(cls, database):
        """

        :param database:
        :return: a random track,
        """
        conn = sqlite3.connect(database)
        c = conn.cursor()
        c.execute("SELECT * FROM track_info ORDER BY RANDOM() LIMIT 1")
        r = c.fetchone()
        if r is None:  # no track in database
            return None
        track = Track(ident=r[0], url=r[1], track=r[2], artist=r[3], album=r[4], duration=r[5], albumart_url=r[6],
                      source=r[7], blacklisted=r[8])
        c.execute("SELECT user from users, log where users.id = log.userid and log.trackid = ? ORDER BY RANDOM() \
LIMIT 1;",
                  (track.ident,))
        r = c.fetchone()
        if r is not None:
            track.user = r[0]
        return track

    def serialize(self):
        return {
            'id': self.ident,
            'url': self.url,
            'title': self.track,
            'artist': self.artist,
            'source': self.source,
            'albumart_url': self.albumart_url,
            'album': self.album,
            'duration': self.duration,
            'blacklisted': self.blacklisted,
            'user': self.user
        }
