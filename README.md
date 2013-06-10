swarm
=====

BitTorrent based deploys using BitTornado based on Twitter's Murder.

###### Make Torrent
`swarm /path/to/file.tar.gz 127.0.0.1:8998 file.tar.gz.torrent`

##### Seed (on 1 server)
`swarm seed file.tar.gz.torrent /path/to/file.tar.gz 127.0.0.1 --port 9000 --verbose`

##### Peer (on other servers)
`swarm peer file.tar.gz.torrent /path/to/file.tar.gz 127.0.0.1 --port 9001 --verbose`
