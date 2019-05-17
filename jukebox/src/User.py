import sqlite3


class User:

    def __init__(self, ident, username, password):
        """

        :param ident: id of the User in database, may be None
        :param username: username of the user
        :param password: sha512 hash of the password

        TODO : This isn't the best of security to do this, and we should modify this.
        """
        self.ident = ident
        self.username = username
        self.password = password

    def __str__(self):
        """

        :return: String self.username
        """
        return self.username

    @classmethod
    def init_from_username(cls, database, username):
        """

        :param database: path to the database
        :param username: username of the user
        :return: None if the user was not found ; User(ident, user, pass) if it exists
        """
        conn = sqlite3.connect(database)
        c = conn.cursor()
        c.execute("SELECT id, user, pass FROM users WHERE user=?",
                  (username,
                   ))
        r = c.fetchone()
        if r is None:
            return None
        assert r[1] == username
        return User(r[0], username, r[2])

    def insert_to_database(self, database):
        """

        :param database: path to the database
        """
        conn = sqlite3.connect(database)
        c = conn.cursor()
        c.execute(
            'INSERT INTO users ("user", "pass") VALUES (?,?)',
            (self.username,
             self.password))
        conn.commit()
