from jukebox import app
app.config.from_pyfile("../config.cfg")
if __name__ == "__main__":
    app.run(host=app.config["LISTEN_ADDR"], port=app.config["LISTEN_PORT"])
