import os
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from IPython import embed
app = Flask(__name__)

#import playpause
import search
#import admin
#import vote
import playlist

if __name__ == "__main__":
    embed()
    search.app.run(host='0.0.0.0', port=8080)