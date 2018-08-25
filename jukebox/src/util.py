from flask import current_app as app
from flask import session, redirect
from functools import wraps
import re, subprocess, socket, os, json


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session or session['user'] is None:
            return redirect("/auth")
        return f(*args, **kwargs)

    return decorated
