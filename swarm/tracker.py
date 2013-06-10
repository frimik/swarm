from BitTornado.BT1.track import track
from BitTornado.HTTPHandler import HTTPHandler
from swarm.utils import spawn
import os

# Monkey-patch.
HTTPHandler.log = lambda *args: None


class Tracker(object):
    def __init__(self, data_file='/tmp/tracker', port=8998):
        self.data_file = data_file
        self.port = port

        try:
            os.unlink(self.data_file)
        except OSError:
            pass

    def start(self):
        spawn(track, ['--dfile', self.data_file, '--port', self.port])