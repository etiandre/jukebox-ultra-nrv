import datetime
from typing import List

from flask_table import Table, Col

from jukebox.src.User import User
from jukebox.src.Track import Track


class StatsUsersTable(Table):
    name = Col('User')
    description = Col('Count')


class StatsTracksTable(Table):
    name = Col('Track')
    description = Col('Count')


class StatsUsersItem(object):
    def __init__(self, user, count):
        self.name = user
        self.description = count


class StatsTracksItem(object):
    def __init__(self, name, count):
        self.name = name
        self.description = count


def create_html_users(database, date=0):
    items = []
    usercounts = User.getUserCounts(database, 10, date=date)
    for couple in usercounts:
        # we get user, count
        user = couple[0]
        count = couple[1]
        items.append(StatsUsersItem(user=user, count=count))

    return StatsUsersTable(items).__html__()


def create_html_tracks(database, date=0):
    items = []
    trackcounts = Track.getTrackCounts(database, 10, date=date)
    for couple in trackcounts:
        # we get user, count
        track = couple[0]
        count = couple[1]
        items.append(StatsTracksItem(name=track, count=count))
    return StatsTracksTable(items).__html__()
