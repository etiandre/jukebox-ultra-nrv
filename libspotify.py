from config import CONFIG

def get_token():
    auth_token = b64encode((CONFIG["spotify-clientid"] + ":" + CONFIG["spotify-secret"]).encode()).decode()
    r = requests.post("https://accounts.spotify.com/api/token", headers={"Authorization": "Basic " + auth_token},
                      data={"grant_type": "client_credentials"})
    return r.json()["access_token"]