from BitTornado.BT1.makemetafile import make_meta_file
from swarm import output


def make_torrent(source_file, torrent_file, tracker):
    """Creates torrent meta file."""
    make_meta_file(source_file, 'http://%s/announce' % tracker, {
        'target': torrent_file,
    })

    output.write('[green][swarm][/green] Source => [white]%s[/white]', source_file)
    output.write('[green][swarm][/green] Tracker => [white]http://%s/announce[/white]', tracker)
    output.write('[green][swarm][/green] Torrent => [white]%s[/white]', torrent_file)