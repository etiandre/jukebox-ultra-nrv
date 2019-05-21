import sqlite3
from typing import List

from flask_table import Table, Col


class StatsUsersTable(Table):
    name = Col('User')
    description = Col('Count')


class StatsUsersItem(object):
    def __init__(self, user, count):
        self.user = user
        self.count = count

def create_html_users_all_time(database):


items: List[StatsUsersItem] = []

for i in range(10):
    # we get user, count
    items.append(StatsUsersItem(user=user, count=count))
    
table = StatsUsersTable(items)


