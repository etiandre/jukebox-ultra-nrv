# Jukebox Ultra NRV mkII

## Prequisites
`python3, python-flask, python-requests,  mpv, youtube-dl, alsa-utils` have to be installed.

## Installation
 - clone the repo
 - move config.py.example to config.py and edit it good sa mère

## Usage
    $ python3 run.py

## Troubleshooting
Check if the service is properly running :
 `$ sudo systemctl status jukebox`
 
Check the logs :
 `$ sudo journalctl -e`
 
Check if youtube-dl is working and up to date
 `youtube-dl https://www.youtube.com/watch?v=6xKWiCMKKJg`

If not, update it : `sudo youtube-dl -U`
