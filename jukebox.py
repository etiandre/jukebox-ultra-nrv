import os
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
app = Flask(__name__)

#import playpause
import search
#import admin
#import vote
#import playlist

@app.route("/")
def accueil():
    return render_template("accueil.html")

if __name__ == "__main__":
    search.app.run(host='0.0.0.0', port=8080)
