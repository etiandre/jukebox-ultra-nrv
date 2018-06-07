import jukebox.src.mpv as mpv
import jukebox.src.idle as idle
import requests
import sys
import threading
import time
class MyMPV(mpv.MPV):
    def __init__(self, argv):
        super().__init__(argv, window_id=None, debug=False)
        self.loaded = threading.Event()
    def on_property_time_pos(self, position=None):
        pass
        
    def load(self, path):
        self.loaded.clear()
        self.command("loadfile", path, "append")
        self.set_property("playlist-pos", 0)
        
    def on_file_loaded(self):
        self.loaded.set()

    def pos(self):
        return self.get_property("time-pos")
    def file(self):
        try:
            return self.get_property("path")
        except mpv.MPVCommandError:
            return None
    
    def finished(self):
        r = None
        try:
            r=self.get_property("eof-reached")
            return r
        except (mpv.MPVCommandError, BrokenPipeError):
            return True

    def play(self):
        self.set_property("pause", False)

    def pause(self):
        self.set_property("pause", True)

    def seek(self, position):
        self.command("seek", position, "absolute")

if __name__ == "__main__":
    url = "http://" + sys.argv[1] + "/sync"
    timeout = int(sys.argv[2])
    player = None
    while True:
        print("idle for {}".format(idle.getIdleSec()))
        if idle.getIdleSec() < timeout:
            if player:
                player.close()
                print("mpv closed")
                player = None
            time.sleep(1)
            continue
        if not player:
            player = MyMPV(["--no-input-default-bindings", "--no-stop-screensaver"])
        orig_t = time.time()
        try:
            sync_data = requests.get(url).json()
        except:
            print("connexion error, retrying...")
            time.sleep(2)
        if len(sync_data["playlist"]) == 0:
            print("playlist empty")
            time.sleep(2)
            continue
        
        if player.file() != sync_data["playlist"][0]["url"]:
            print("loading new track")
            player.load(sync_data["playlist"][0]["url"])
            player.pause()
            player.loaded.wait()
            print("loaded")
        else:
            local = player.pos()
            remote = sync_data["time"]
            delay = time.time()-orig_t
            delta = remote - local
            offset = 0.5
            # print("local: {} | remote : {} | delta {} | delay {}".format(local, remote, delta, delay))
            if abs(delta) >= offset: # catch up
                print("catching up")
                player.seek(remote + delay + offset/2) # go ahead
            elif delta > 0.001: # sync
                print("en avance de {}".format(delta))
                player.pause()
                time.sleep(abs(delta+delay)/2)
                player.play()
                
            player.play()
        time.sleep(1)
    mpv.close()
