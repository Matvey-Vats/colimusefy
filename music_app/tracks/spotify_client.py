import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

def get_spotify_client():
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
        client_id='e390e1df56de4c979949fcae69ae5661',
        client_secret='436a5e6e92b741f1bdbed020dcdf7e23'
    ))
    return sp