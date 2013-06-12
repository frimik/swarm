from BitTornado.download_bt1 import BT1Download, defaults, get_response
from BitTornado.RawServer import RawServer
from BitTornado.bencode import bencode
from BitTornado import createPeerID
from swarm.concurrent import spawn_later, Event
from swarm.tracker import Tracker
from swarm import output
from datetime import datetime, timedelta
import hashlib
import random


class Client(object):
    def __init__(self, torrent_file, destination_file, ip, port, is_seed=False, verbose=True):
        self.torrent_file = torrent_file
        self.destination_file = destination_file
        self.ip = ip
        self.port = port
        self.is_seed = is_seed
        self.verbose = verbose

        self.id = createPeerID()

        self.done_flag = Event()
        self.finished_at = None

        # Client statistics.
        self.percent_done = 0.0
        self.download_rate = 0.0
        self.upload_rate = 0.0
        self.time_estimate = 0.0

        # Torrent statistics.
        self.ratio = 0.0
        self.upload_total = 0.0
        self.download_total = 0.0
        self.distributed_copies = 0.0
        self.peers_percent_done = 0.0
        self.torrent_rate = 0.0
        self.num_peers = 0
        self.num_seeds = 0
        self.num_old_seeds = 0

        # Activity message.
        self.activity = None

        if is_seed:
            # Seed is also the tracker.
            output.write('[green][swarm][/green] [white]starting tracker[/white]')
            self.tracker = Tracker(port + 1000)
            self.tracker.start()

        # Start the shutdown checker.
        self.maybe_shutdown()

    def maybe_shutdown(self):
        """Shutsdown if no peers have connected within 5 seconds of finishing."""
        if self.num_peers == 0 and \
                (self.finished_at and self.finished_at < datetime.now() - timedelta(seconds=5)) and \
                (not self.is_seed or self.tracker.leechers == 0):
            self.done_flag.set()
        else:
            spawn_later(1, self.maybe_shutdown)

    def on_finish(self):
        self.finished_at = datetime.now()
        self.percent_done = 100.0
        self.download_rate = 0.0
        self.activity = 'seeding'

    def on_fail(self):
        self.finished_at = datetime.now()
        self.percent_done = 0.0
        self.download_rate = 0.0
        self.activity = 'failed'
        self.done_flag.set()

    def on_error(self, msg):
        output.write('[red]%s[/red]', msg)
        self.done_flag.set()

    def on_exception(self, excmsg):
        output.write('[red]%s[/red]', excmsg)

    # noinspection PyUnusedLocal
    def on_status(self, dpflag=Event(), fractionDone=None, timeEst=None, downRate=None, upRate=None,
                  statistics=None, spew=None, sizeDone=None, activity=None):
        if fractionDone is not None:
            if self.finished_at:
                self.percent_done = 100.0
            else:
                self.percent_done = float(int(fractionDone * 1000)) / 10

        if timeEst is not None:
            self.time_estimate = timeEst

            m, s = divmod(timeEst, 60)
            h, m = divmod(m, 60)

            self.activity = 'downloading '

            # Format time.
            if h > 0:
                self.activity += '%dh%02dm%02ds' % (h, m, s)
            elif m > 0:
                self.activity += '%dm%02ds' % (m, s)
            else:
                self.activity += '%02ds' % s

        if activity is not None:
            self.activity = activity

        if downRate is not None:
            self.download_rate = float(downRate) / (1 << 10)

        if upRate is not None:
            self.upload_rate = float(upRate) / (1 << 10)

        if statistics is not None:
            self.ratio = statistics.shareRating
            self.upload_total = float(statistics.upTotal) / (1 << 20)
            self.download_total = float(statistics.downTotal) / (1 << 20)
            self.num_peers = statistics.numPeers
            self.num_old_seeds = statistics.numOldSeeds
            self.num_seeds = statistics.numSeeds
            self.distributed_copies = 0.001 * int(1000 * statistics.numCopies)
            self.torrent_rate = float(statistics.torrentRate) / (1 << 10)
            self.peers_percent_done = statistics.percentDone

        if self.activity and self.verbose:
            if self.is_seed and self.finished_at:
                output.write('[green][swarm][/green] [white]%.2f%%[/white] '
                             '(torrent: [white]%.1f[/white] kb/s peers: [white]%d[/white] seeds: [white]%d[/white]) '
                             '[yellow]%s[/yellow]',
                             self.peers_percent_done, self.torrent_rate, self.num_peers, self.num_seeds, self.activity)
            else:
                output.write('[green][swarm][/green] [white]%.2f%%[/white] '
                             '(down: [white]%.1f[/white] kb/s up: [white]%.1f[/white] kb/s '
                             'peers: [white]%d[/white] seeds: [white]%d[/white]) [yellow]%s[/yellow]',
                             self.percent_done, self.download_rate, self.upload_rate, self.num_peers,
                             self.num_seeds, self.activity)

        # Format downloader that displaying finished.
        dpflag.set()

    def start(self):
        rawserver = None

        try:
            config = {k: v for k, v, _ in defaults}
            config['ip'] = self.ip
            config['responsefile'] = self.torrent_file
            config['saveas'] = self.destination_file

            random.seed(self.id)

            rawserver = RawServer(
                doneflag=self.done_flag,
                timeout_check_interval=config['timeout_check_interval'],
                timeout=config['timeout'],
                ipv6_enable=config['ipv6_enabled'],
                failfunc=self.on_fail,
                errorfunc=self.on_exception)
            rawserver.bind(
                port=self.port,
                bind=config['bind'],
                reuse=True,
                ipv6_socket_style=config['ipv6_binds_v4'])

            # Download torrent metadata.
            response = get_response(
                file=config['responsefile'],
                url=config['url'],
                errorfunc=self.on_error)

            # Bail if tracker is done.
            if not response:
                return

            dow = BT1Download(
                statusfunc=self.on_status,
                finfunc=self.on_finish,
                errorfunc=self.on_error,
                excfunc=self.on_exception,
                doneflag=self.done_flag,
                config=config,
                response=response,
                infohash=hashlib.sha1(bencode(response['info'])).digest(),
                id=self.id,
                rawserver=rawserver,
                port=self.port)

            if not dow.saveAs(lambda default, size, saveas, dir: saveas if saveas else default):
                return

            if not dow.initFiles(old_style=True):
                return

            if not dow.startEngine():
                dow.shutdown()
                return

            dow.startRerequester()
            dow.autoStats()

            if not dow.am_I_finished():
                self.on_status(activity='connecting to peers')

            rawserver.listen_forever(dow.getPortHandler())

            self.on_status(activity='shutting down')

            dow.shutdown()
        finally:
            if rawserver:
                rawserver.shutdown()

            if not self.finished_at:
                self.on_fail()