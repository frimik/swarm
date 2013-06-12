swarm
=====

BitTorrent based deploys using BitTornado based on Twitter's Murder.

###### Make Torrent
`swarm /path/to/file.tar.gz <seed ip>:<seed port + 1000> file.tar.gz.torrent`

###### Seed (on 1 server)
`swarm seed file.tar.gz.torrent /path/to/file.tar.gz <seed ip> --port 7998 --verbose`

###### Peer (on other servers)
`swarm peer file.tar.gz.torrent /path/to/file.tar.gz <peer ip> --port 7999`
