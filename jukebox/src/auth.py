from flask import Blueprint, render_template, redirect, session, request, flash
from flask import current_app as app
import sqlite3, hashlib

from jukebox.src.User import User
from jukebox.src.util import *
auth = Blueprint('auth', __name__)


@auth.route("/auth", methods=['GET', 'POST'])
def auth_page():
    conn = sqlite3.connect(app.config["DATABASE_PATH"])
    c = conn.cursor()

    if request.method == 'GET':
        # If the user is already logged in, redirect them to the app
        if "user" in session and session['user'] is not None:
            return redirect("/app")
        else:  # else, render login form
            return render_template("auth.html")

    # handle account creation
    success = False
    if request.form["action"] == "new":
        # we must first check if the username isn't aleady taken
        # then we do as usual
        # if it is, display a notification
        user = User.init_from_username(app.config["DATABASE_PATH"], request.form["user"])
        if user is not None:
            flash("Account already exists")
            return render_template("auth.html")
        user = User(None, request.form["user"], hashlib.sha512(request.form["pass"].encode()).hexdigest())
        user.insert_to_database(app.config["DATABASE_PATH"])
        app.logger.info("Created account for %s", request.form["user"])
        session['user'] = request.form['user']
        return redirect("/app")

    else:  # handle login
        user = User.init_from_username(app.config["DATABASE_PATH"], request.form["user"])
        if user is not None and user.password == hashlib.sha512(request.form["pass"].encode()).hexdigest():
            app.logger.info("Logging in {}".format(request.form["user"]))
            session['user'] = request.form['user']
            return redirect("/app")
        else:
            flash("Raté")
            app.logger.info("Failed log attempt for %s", request.form["user"])
    # if account successfully created OR login successful
    return render_template("auth.html")


@auth.route("/logout", methods=['GET', 'POST'])
@requires_auth
def logout():
    if request.method == "POST":
        session['user'] = None
        return redirect("/auth")
    else:
        return render_template("logout.html", user=session["user"])
