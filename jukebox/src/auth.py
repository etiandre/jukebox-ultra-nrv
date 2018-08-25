from flask import Blueprint, render_template, redirect, session, request, flash
from flask import current_app as app
import sqlite3, hashlib
from jukebox.src.util import *
auth = Blueprint('auth', __name__)


@auth.route("/auth", methods=['GET', 'POST'])
def auth_page():
    conn = sqlite3.connect(app.config["DATABASE_PATH"])
    c = conn.cursor()

    if request.method == 'GET':
        # If the user is aready logged, redirect it to the app
        if "user" in session and session['user'] is not None:
            return redirect("/app")
        else: # else, render login form
            return render_template("auth.html")

    # handle account creation
    success = False
    if request.form["action"] == "new":
        try:
            c.execute(
                'INSERT INTO users VALUES (?,?)',
                (request.form["user"],
                 hashlib.sha512(request.form["pass"].encode()).hexdigest()))
            conn.commit()
            app.logger.info("Created account for %s", request.form["user"])
            success = True
        except sqlite3.IntegrityError:
            app.logger.info("Account already exists for %s",
                            request.form["user"])
            flash("T'as déjà un compte gros malin")
    else: # handle login
        c.execute("SELECT user FROM users WHERE user=? AND pass=?",
                  (request.form["user"],
                   hashlib.sha512(request.form["pass"].encode()).hexdigest()))
        if c.fetchone() != None:
            app.logger.info("Logging in %s using password",
                            request.form["user"])
            success = True
        else:
            flash("Raté")
            app.logger.info("Failed log attempt for %s", request.form["user"])
    # if account successfully created OR login successful
    if success == True:
        session['user'] = request.form['user']
        return redirect("/app")
    return render_template("auth.html")


@auth.route("/logout", methods=['GET', 'POST'])
@requires_auth
def logout():
    if request.method == "POST":
        session['user'] = None
        return redirect("/auth")
    else:
        return render_template("logout.html", user=session["user"])
