# soundcloud-downloader
download soundcloud mp3s hosted on their cdn

## setup
`pip install eyed3 requests bs4`

## usage
```
py download.py -s [link to song or set url] -cid [client id]
```
`-s` is required where as if you do not supply a client id using `-cid` one will be generated for you.
