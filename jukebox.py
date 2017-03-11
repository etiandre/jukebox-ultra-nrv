import os
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

app = Flask(__name__)

# exemple
@app.route("/")
def message_sympa():
    return "coucou"
