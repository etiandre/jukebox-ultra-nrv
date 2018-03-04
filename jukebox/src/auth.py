from flask import Blueprint, render_template, redirect, session, request, flash
from flask import current_app as app
import sqlite3, hashlib
from jukebox.src.util import *
auth = Blueprint('auth', __name__)


@auth.route("/auth", methods=['GET', 'POST'])
def auth_page():
    conn = sqlite3.connect("jukebox.sqlite3")
    c = conn.cursor()
    mac = get_mac(request.remote_addr)
    session["mac"] = mac

    if request.method == 'GET':
        # if already logged
        if "user" in session and session['user'] is not None:
            return redirect("/app")
        c.execute("SELECT * FROM macs WHERE mac=?", (session["mac"], ))
        r = c.fetchone()
        # if mac saved
        if r is not None:
            session["user"] = r[0]
            return redirect("/app")
        else:
            return render_template("auth.html")

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
    else:
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
    if success == True:
        session['user'] = request.form['user']
        c.execute("REPLACE INTO macs (user, mac) VALUES (?,?)",
                  (request.form["user"], session["mac"]))
        conn.commit()
        return redirect("/app")
    return render_template("auth.html")


@auth.route("/logout", methods=['GET', 'POST'])
@requires_auth
def logout():
    if request.method == "POST":
        app.logger.info("Unassociating %s and %s", session['user'],
                        session['mac'])
        conn = sqlite3.connect("jukebox.sqlite3")
        c = conn.cursor()
        c.execute("DELETE FROM macs WHERE user=? AND mac=?",
                  (session["user"], session["mac"]))
        conn.commit()
        session['user'] = None
        session['mac'] = None
        return redirect("/auth")
    else:
        return render_template("logout.html", user=session["user"])
