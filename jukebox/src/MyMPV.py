#import threading

import mpv


class MyMPV(mpv.MPV):
    def __init__(self, argv, video=False):
        super().__init__(video=video)#, start_event_thread=False)

        self.playlist_pos = 0
        self.ended = False
