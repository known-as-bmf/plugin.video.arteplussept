from xbmcswift2 import xbmc
from xbmcswift2 import ListItem

class Player(xbmc.Player):
    
    def __init__(self):
        super(Player, self).__init__()
    
    def isPlayback(self): # rename to is_playback
        try:
            return self.isPlaying() and self.isPlayingVideo() and self.getTime() >= 0
        except Exception:
            return False
       
    def onAVStarted(self):
        print('LED Status started AV')
        # Will be called when playback starts and all player properties are updated
        # Not really needed since Plugin might be triggered after playback starts?
        pass
    
    def start_playback(self):
        # send up next information
        pass
    
    def onPlayBackStopped(self):
        # Will be called when user stops playing a file.
        print('LED Status stopped')
        self.stop_playback()
        pass
    
    def onPlayBackEnded(self):
        # Will be called when kodi stops playing a file.
        print('LED Status stopped')
        self.stop_playback()
        pass
    
    def onPlayBackError(self):
        # Will be called when kodi stops playing a file.
        print('LED Status error')
        pass
    
    def onPlayBackPaused(self):
        # Will be called when kodi stops playing a file.
        print('LED Status paused')
        pass

    def stop_playback(self):
        # code that should run everytime playback stops.
        pass
        
    def signal_callback(self, data):
        pass
    