from flask import current_app as app
from flask import session, redirect
from functools import wraps
import re
import subprocess
import alsaaudio


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session or session['user'] is None:
            return redirect("/auth")
        return f(*args, **kwargs)

    return decorated


def get_volume():
    """
    Example of amixer output :
    Simple mixer control 'Master',0
  Capabilities: pvolume pswitch pswitch-joined
  Playback channels: Front Left - Front Right
  Limits: Playback 0 - 65536
  Mono:
  Front Left: Playback 40634 [62%] [on]
  Front Right: Playback 40634 [62%] [on]
    """
    m = alsaaudio.Mixer()
    return int(m.getvolume()[0])


def set_volume(volume):
    try:
        if int(volume) < 0 or int(volume) > 100:
            app.logger.warning("Error, volume {} incorrect".format(volume))
            return
    except ValueError:
        app.logger.warning("Error, volume {} incorrect".format(volume))
        return
    m = alsaaudio.Mixer()
    m.setvolume(int(volume))
    app.logger.info("Volume set to %s", get_volume())
