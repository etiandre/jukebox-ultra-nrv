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
        print("La playlist {} vient d'être ajoutée. Son id est {}.".format(playlist.name, idplaylist))

    def remove_playlist(self, idplaylist): #idPlaylist is an integer
        if self.listPlaylists[idplaylist] == False or idplaylist > self.nbPlaylists:
            print("Cet id de playlist n'est pas attribué.")
        else:
            self.listPlaylists[idplaylist] = False
            self.nbPlaylists -= 1
            print("La playlist {} a été supprimée.".format(idplaylist))

    def to_string(self):
        print("Playlists disponibles :")
        for pl in self.listPlaylists:
            if pl != False:
                print("{} : {}".format(pl.id, pl.name))

PlaylistList = ListPlaylist()

##Playlist ##############################################
class Playlist:
    def __init__(self, name, idplaylist):
        self.nbTracks = 0
        self.listTracks = []
        self.name = name             #Don't use the constructor to build a playlist
        self.id = idplaylist         #Use new_playlist('name') instead

    def add_track(self, track):
        self.listTracks.append(url(track))        #Using the url returned by the search function
        self.nbTracks += 1
        print("La track {} a bien été ajoutée dans la playlist {} à la position {}.".format(track, self.name, self.nbTracks))

    def remove_track(self, pos_track): #pos_track is the position of a song in a queue
        del self.listTracks[pos_track-1]
        self.nbTracks -= 1
        print("La track en position {} a bien été retirée de la playlist {}.".format(pos_track, self.name)) #To update if I have access to the deleted track's name


    def to_string(self):
        print("Tracks dans la playlist :")
        for pos in range(self.nbTracks):
            print("{} : {}".format(pos, self.listTracks[pos].name))          #Assuming Track is an object with a 'name' variable


def new_playlist(name):
    idplaylist = PlaylistList.first_void()
    P = Playlist(name, idplaylist)
    PlaylistList.add_playlist(P)
    print("La playlist {} a bien été crée. Son id est {}.".format(P.name, P.id))
    return P


#Flask things
@app.route("/playlist/list")
def list():
    """Returns available playlists"""
    PlaylistList.to_string()

@app.route("/playlist/<id>")
def show_playlist(id):
    """Returns the id playlist content"""
    if id < PlaylistList.nbPlaylists and PlaylistList.listPlaylists[id] != False:
        PlaylistList.listPlaylists[id].to_string()
    else:
        print("Cette playlist n'existe pas, voulez-vous en créer une ?")

@app.route("/playlist/add", methods=["POST"])
def add_playlist():
    """Creates a playlist and adds it to the playlist list"""
    name = input("Le nom de la playlist :")
    P = new_playlist(name)

@app.route("/playlist/<id>/remove")
def remove_playlist(id):
    """Deletes the id playlist"""
    if id < PlaylistList.nbPlaylists and PlaylistList.listPlaylists[id] != False:
        PlaylistList.remove_playlist(id)
    else:
        print("Cette playlist n'existe pas, ou a déjà été supprimée.")

@app.route("/playlist/<id>/add", methods=["POST"])
def add_track_to_playlist(id):
    """Adds track to playlist"""
    if id < PlaylistList.nbPlaylists and PlaylistList.listPlaylists[id] != False:
        p = PlaylistList.listPlaylists[id]
        track_name = input("Quelle track à ajouter à la playlist {} ?".format(p.name))
        p.add_track(track_name)
    else:
        print("Cette playlist n'existe pas, voulez-vous en créer une ?")

@app.route("/playlist/<id>/remove", methods=["POST"])
def remove_track_from_playlist(id):
    """Removes the nth track queued from playlist"""
    if id < PlaylistList.nbPlaylists and PlaylistList.listPlaylists[id] != False:
        p = PlaylistList.listPlaylists[id]
        try:
            track_pos = int(input("Quel nème track à retirer à la playlist {} ?".format(p.name)))
            if 0 < track_pos <= p.nbTracks:
                p.remove_track(track_pos)
            else:
                print("Position de track invalide.")
        except ValueError:
            print('Nombre invalide.')
    else:
        print("Cette playlist n'existe pas, voulez-vous en créer une ?")



@app.route("/playlist/<id>/move", methods=["POST"])
def move_track(id):
    """Move a track in the queue """
    if id < PlaylistList.nbPlaylists and PlaylistList.listPlaylists[id] != False:
        p = PlaylistList.listPlaylists[id]
        try:
            track_pos = int(input("Quel nème track à déplacer dans la playlist {} ?".format(p.name)))
            new_pos = int(input("A quelle position la mettre dans la playlist {} ?".format(p.name)))
            if 0 < track_pos <= p.nbTracks and 0 < track_pos <= p.nbTracks:
                track = p.listTracks[track_pos-1]
                p.remove_track(track_pos)
                p.listTracks.insert(new_pos-1, track)
            else:
                print("Position de track invalide.")
        except ValueError:
            print('Nombre invalide.')
    else:
        print("Cette playlist n'existe pas, voulez-vous en créer une ?")