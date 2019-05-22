import sqlite3
import random
import sys

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
        :param user: may be None, else it means we get it from a log and it is a str
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
    def does_track_exist(cls, database, url):
        """

        :param database:
        :param url:
        :return:
        """
        conn = sqlite3.connect(database)
        c = conn.cursor()
        # check if track not in track_info i.e. if url no already there
        c.execute("""select id
                     from track_info
                     where url = ?;
                  """,
                  (url,))
        r = c.fetchall()
        return not not r

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
        r = c.fetchone()
        if r is None:
            return None
        return Track(ident=r[0], url=r[1], track=r[2], artist=r[3], album=r[4], duration=r[5],
                     albumart_url=r[6], source=r[7], blacklisted=r[8])

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

    @classmethod
    def insert_track(cls, database, track_form):
        """

        :param database:
        :param track:
        :return:
        """
        conn = sqlite3.connect(database)
        c = conn.cursor()
        c.execute("""INSERT INTO track_info
                            (url, track, artist, album, duration, albumart_url,
                            source) VALUES
                            (?,   ?,     ?,      ?,     ?,        ?,
                            ?)
                            ;""",
                  (track_form["url"], track_form["title"], track_form["artist"],
                   track_form["album"], track_form["duration"],
                   track_form["albumart_url"], track_form["source"]))
        conn.commit()

    @classmethod
    def refresh_by_url(cls, database, url):
        """

        :param database: Database used
        :param url: URL of the track (str)
        """
        app.logger.info(url)
        track = cls.import_from_url(database, url)
        # check if source is loaded
        if 'jukebox.src.backends.search.'+track.source not in sys.modules:
            return
        for search in app.search_backends:
            if search.__name__ == 'jukebox.src.backends.search.'+track.source:
                break
        track_dict = search.search_engine(url, use_youtube_dl=True)[0]
        app.logger.info("Track dict : ", track_dict)
        track = Track(None, url, track_dict["title"], track_dict["artist"], track_dict["source"],
                      track_dict["albumart_url"], album=track_dict["album"], duration=track_dict["duration"])

        conn = sqlite3.connect(database)
        c = conn.cursor()
        c.execute("""UPDATE track_info
SET track = ?, artist = ?, albumart_url = ?, album = ?, duration = ?
WHERE url = ?
                  """,
                  (track.track, track.artist, track.albumart_url, track.album, track.duration, url,))
        conn.commit()

    def insert_track_log(self, database, user):
        """
        As it creates a log, it also updates the value of self.useré

        :param database:
        :param user:
        :return:
        """
        conn = sqlite3.connect(database)
        c = conn.cursor()
        self.user = user
        c.execute("""select id
                             from users
                             where user = ?;
                          """,
                  (user,))

        r = c.fetchall()
        # print(r)
        user_id = r[0][0]
        c.execute("INSERT INTO log(trackid,userid) VALUES (?,?)",
                  (self.ident, user_id))
        conn.commit()

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
            'user': self.user,
            'randomid': random.randint(1, 999_999_999_999)  # to identify each track in the playlist
            # even if they have the same url
        }
