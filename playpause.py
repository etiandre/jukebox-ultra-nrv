# -*- coding: utf-8 -*-
import os
from jukebox import app, render_template
import time
from playlist import ListPlaylist, Playlist, PlaylistList, request


def play_track(track):
    os.system("mpc -h {} play".format(ip))      # TODO : cmt on envoie le morceau à mopidy ? :'(


def play_playlist(idplaylist):                    # Request playlist has +1 priority
    """ Starts playing the playlist while giving a priority to the request playlist """
    while True:
        while request.nbTracks > 0:
            track = request.listTracks[0]
            play_track(track)
            request.next_song()
            time.sleep(track.length)
        playlist = PlaylistList[id]
        if playlist == False:
            print("La playlist d'id {} n'existe pas.".format(idplaylist))
        else:
            if Playlist.nbTracks == 0:
                pass
            elif Playlist.nbTracks <0:
                print("Erreur : la playlist d'id {} a un nombre de tracks négatif ?!".format(idplaylist))
            else:
                track = playlist.listTracks[0]
                play_track(track)
                playlist.next_song()
                time.sleep(track.length)


@app.route("/")
def message_sympa():
    return render_template('hello.html')


@app.route("/play")
def play():
    os.system("mpc -h {} play".format(ip))


@app.route("/play/<id>")
def play_playlist2():
    play_playlist(id)
    return render_template('play.html')         # TODO : the play website


@app.route("/pause")
def pause():                                    # TODO : check if it breaks the play_playlist function
    os.system("mpc -h 192.168.1.115 pause")
    return render_template('pause.html')