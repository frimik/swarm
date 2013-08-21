from BitTornado.BT1.track import defaults, Tracker as _Tracker
from BitTornado.HTTPHandler import HTTPHandler as _HTTPHandler
from BitTornado.RawServer import RawServer
from swarm.concurrent import Event, spawn
import tempfile


class HTTPHandler(_HTTPHandler):
    def log(self, ip, ident, username, header, responsecode, length, referrer, useragent):
        # Silence this because its pointless...
        pass


class Tracker(object):
    def __init__(self, port):
        self.port = port
        self._tracker = None

    def start(self):
        config = dict([(v[0], v[1]) for v in defaults])
        config['dfile'] = tempfile.mktemp()  # Use temporary file since it won't be reused.
        config['port'] = self.port

        rawserver = RawServer(
            doneflag=Event(),
            timeout_check_interval=config['timeout_check_interval'],
            timeout=config['socket_timeout'],
            ipv6_enable=config['ipv6_enabled'])
        rawserver.bind(
            port=config['port'],
            bind=config['bind'],
            reuse=True,
            ipv6_socket_style=config['ipv6_binds_v4'])

        self._tracker = _Tracker(config, rawserver)

        # Spawn in separate thread.
        spawn(rawserver.listen_forever, HTTPHandler(self._tracker.get, config['min_time_between_log_flushes']))

    @property
    def seeds(self):
        """Returns number of peers that have fully downloaded the torrent."""
        return sum(self._tracker.seedcount.values())

    @property
    def leechers(self):
        """Returns number of peers that are still downloading the torrent."""
        leechers = 0
        for torrent in self._tracker.downloads.values():
            leechers += len([leecher for leecher in torrent.values() if leecher['left'] > 0])
        return leechers
