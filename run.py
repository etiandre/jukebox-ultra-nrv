from jukebox import app
import os
app.config.from_pyfile("../config.cfg")
if __name__ == "__main__":
    if os.path.exists("mpv.socket"):
        os.remove("mpv.socket")
    app.run(host=app.config["LISTEN_ADDR"], port=app.config["LISTEN_PORT"])
