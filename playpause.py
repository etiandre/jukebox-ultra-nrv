import os
from jukebox import app, render_template

@app.route("/")
def message_sympa():
    return render_template('hello.html')

@app.route("/play")
def play():
    os.system("mpc -h 192.168.1.115 play")
    return render_template('play.html')

@app.route("/pause")
def pause():
    os.system("mpc -h 192.168.1.115 pause")
    return render_template('pause.html')