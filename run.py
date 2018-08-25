from jukebox import app
import os
app.config.from_pyfile("../config.cfg")
if __name__ == "__main__":
    # cleanup leftovers
    if os.path.exists("mpv.socket"):
        os.remove("mpv.socket")
    # create database if it doesn't exists
    if not os.path.exists(app.config["DATABASE_PATH"]):
        print("Databse nonexistent, creating schema")
        import sqlite3
        conn = sqlite3.connect(app.config["DATABASE_PATH"])
        c = conn.cursor()
        c.execute("""
        CREATE TABLE "users" (
            "user" TEXT NOT NULL PRIMARY KEY,
            "pass" TEXT
        );
        """)
        c.execute("""CREATE TABLE "track_info" (
            "url" TEXT NOT NULL,
            "track" TEXT,
            "artist" TEXT,
            "album" TEXT,
            "duration" TEXT,
            "albumart_url" TEXT
        );
        """)
        c.execute("""CREATE TABLE log (
            "id" INTEGER PRIMARY KEY,
            "track" TEXT NOT NULL,
            "time" INTEGER NOT NULL DEFAULT CURRENT_TIMESTAMP,
            "user" TEXT NOT NULL
        );
        """)
        conn.commit()
        conn.close()

    # run the flask app
    app.run(host=app.config["LISTEN_ADDR"], port=app.config["LISTEN_PORT"])
