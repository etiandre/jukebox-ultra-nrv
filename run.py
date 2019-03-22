from jukebox import app
import os
if __name__ == "__main__":
    # cleanup leftovers
    if os.path.exists("mpv.socket"):
        os.remove("mpv.socket")
    # create database if it doesn't exists
    if not os.path.exists(app.config["DATABASE_PATH"]):
        app.logger.info("Databse nonexistent, creating schema")
        import sqlite3
        conn = sqlite3.connect(app.config["DATABASE_PATH"])
        c = conn.cursor()
        with open("jukebox/src/schema-users.sql", 'r') as f:
            schema_users = f.read()
        with open("jukebox/src/schema-log.sql", 'r') as f:
            schema_log = f.read()
        with open("jukebox/src/schema-track-info.sql", 'r') as f:
            schema_track_info = f.read()
        c.execute(schema_users)
        c.execute(schema_log)
        c.execute(schema_track_info)
        conn.commit()
        conn.close()

    # run the flask app
    app.run(host=app.config["LISTEN_ADDR"], port=app.config["LISTEN_PORT"])
