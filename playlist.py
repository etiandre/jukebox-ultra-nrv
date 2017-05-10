"""
Ce module s'occupe de gérer les playlists et l'édition de celles-ci
"""
from jukebox import app

#Python code

##ListPlaylist ##########################################
class ListPlaylist:
    """ The List of all playlists """
    def __init__(self):
        self.nbPlaylists = 0
        self.listPlaylists = []

    def is_full(self):
        res = True
        for x in self.listPlaylists:
            if x == False:
                res = False
        return res

    def first_void(self):
        """ Returns the first open slot of the playlist list """
        counter = 0
        while self.listPlaylists[counter] != False:
            counter += 1
        return counter

    def add_playlist(self, playlist):
        idplaylist = self.first_void()
        if idplaylist >= self.nbPlaylists :
            self.listPlaylists.append(playlist)
        else:
            self.listPlaylists[idplaylist] = playlist
        self.nbPlaylists += 1
        print("La playlist {} vient d'être ajoutée. Son id est {}.".format(playlist.name, idPlaylist))

    def remove_playlist(self, idPlaylist): #idPlaylist is an integer
        if self.listPlaylists[idPlaylist] == False or idPlaylist > self.nbPlaylists:
            print("Cet id de playlist n'est pas attribué.")
        else:
            self.listPlaylists[idPlaylist] = False
            self.nbPlaylists -= 1
            print("La playlist {} a été supprimée.".format(idPlaylist))

    def to_string(self):
        for pl in self.listPlaylists:
            print(pl.name)

PlaylistList = ListPlaylist()

##Playlist ##############################################
class Playlist:
    def __init__(self, name, idplaylist):
        self.nbTracks = 0
        self.listTracks = []
        self.name = name        #Don't use the constructor to build a playlist
        self.id = idplaylist         #Use new_playlist('name') instead

    def add_track(self, track):
        self.listTracks.append(url(track))        #Using the url returned by the search function
        self.nbTracks += 1
        print("La track {} a bien été ajoutée dans la playlist {} à la position {}.".format(track, self.name, self.nbTracks))

    def remove_track(self, pos_track): #pos_track is the position of a song in a queue
        del self.listTracks[pos_track-1]
        self.nbTracks -= 1
        print("La track en position {} a bien été retirée de la playlist {}.".format(pos_track, self.name) #To update if I have access to the deleted track's name


    def to_string(self):
        for tr in self.listTracks:
            print(tr.name)          #Assuming Track is an object with a 'name' variable


def new_playlist(name):
    idplaylist = PlaylistList.first_void()
    P = Playlist(name, idplaylist)
    PlaylistList.add_playlist(P)
    return P


#Flask things
@app.route("/playlist/list")
def list():
    """Returns available playlist"""
    PlaylistList.to_string()

@app.route("/playlist/<id>")
def show_playlist(id):
    """renvoie le contenu de la playlist correspondant à id"""
    pass

@app.route("/playlist/<id>/add", methods=["POST"])
def add_track_to_playlist(id):
    """ajoute la track dans la playlist"""
    pass

@app.route("/playlist/<id>/remove", methods=["POST"])
def remove_track_from_playlist(id):
    """supprime la track depuis la playlist"""
    pass

@app.route("/playlist/<id>/move", methods=["POST"])
def move_track(id):
    """échange deux tracks dans une playlists (change l'ordre)"""
    pass