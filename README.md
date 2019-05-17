# Jukebox Ultra NRV mkIII

## Prequisites
`python3, python-flask, python-requests,  mpv, youtube-dl, alsa-utils,
python3-pip` have to be installed.
Also from pip, get `youtube_dl`, `passlib` and `flask-WTF`

## Installation

 - clone the repo
 - move config.py.example to config.py and edit it 😎
 - To add a favicon, place it in the `jukebox/static` folder
 - Install requirements using `pip install -r requirements.py`

## Usage

```bash
$ python3 run.py
```

or with a systemd service jukebox

```bash
$ systemctl start jukebox.service
```

## Security

The current use of this application is only among a "friendly" and local network.
As such, we haven't yet focused much on security.
The passwords are stored using pbkdf2_sha256 from library `passlib`.

## Troubleshooting

If you are using a systemctl service.
Check if the service is properly running :
 `$ sudo systemctl status jukebox`
 
Check the logs :
 `$ sudo journalctl -u jukebox.service`
 
Check if youtube-dl is working and up to date
 `youtube-dl https://www.youtube.com/watch?v=6xKWiCMKKJg`

If not, update it : `sudo youtube-dl -U`


## Development

For the logs, please use `app.logger.info`, `app.logger.warning` or `app.logger.error`.
