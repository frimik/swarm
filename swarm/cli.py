"""Swarm.

Usage:
  swarm torrent <source> <tracker> <torrent>
  swarm seed <torrent> <destination> <ip> [--port=<port>] [--timeout=N] [--verbose]
  swarm peer <torrent> <destination> <ip> [--port=<port>] [--timeout=N] [--verbose]

Options:
  -h --help      Show this screen.
  --verbose      Constantly print status information.
  --port=<port>  Port peer should listen on. [default: 7998].
  --timeout=<s>  Number of seconds to seed after last leecher disconnected. [default: 5].
"""
from docopt import docopt
from swarm.client import Client
from swarm.torrent import make_torrent


def main():
    arguments = docopt(__doc__)

    if arguments['torrent']:
        make_torrent(
            source_file=arguments['<source>'],
            torrent_file=arguments['<torrent>'],
            tracker=arguments['<tracker>'])
    else:
        client = Client(
            torrent_file=arguments['<torrent>'],
            destination_file=arguments['<destination>'],
            is_seed=arguments['seed'],
            verbose=arguments['--verbose'],
            ip=arguments['<ip>'],
            peer_timeout=int(arguments['--timeout']),
            port=int(arguments['--port']))
        client.start()

if __name__ == '__main__':
    main()
