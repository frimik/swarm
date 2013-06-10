"""Swarm.

Usage:
  swarm torrent <file> <tracker> <torrent>
  swarm seed <torrent> <file> <ip> [--port=<port>] [--verbose]
  swarm peer <torrent> <file> <ip> [--port=<port>] [--verbose]

Options:
  -h --help      Show this screen.
  --verbose      Constantly print status information.
  --port=<port>  Port to listen on. [default: 54321].
"""
from docopt import docopt
from colors import white, green


def run():
    arguments = docopt(__doc__)

    if arguments['torrent']:
        from BitTornado.BT1.makemetafile import make_meta_file

        dist_file = arguments['<file>']
        torrent = arguments['<torrent>']
        tracker = arguments['<tracker>']

        make_meta_file(dist_file, 'http://%s/announce' % tracker, {
            'target': torrent,
        })

        print '%s File => %s' % (green('[swarm]'), white(dist_file))
        print '%s Tracker => %s' % (green('[swarm]'), white('http://%s/announce' % tracker))
        print '%s Torrent => %s' % (green('[swarm]'), white(torrent))
    elif arguments['peer'] or arguments['seed']:
        from . import client
        from .tracker import Tracker

        if arguments['seed']:
            print '%s %s' % (green('[swarm]'), white('starting tracker'))
            tracker = Tracker()
            tracker.start()

        client.run(
            torrent_file=arguments['<torrent>'],
            saveas=arguments['<file>'],
            ip=arguments['<ip>'],
            is_seed=arguments['seed'],
            verbose=arguments['--verbose'],
            port=int(arguments['--port']),
        )