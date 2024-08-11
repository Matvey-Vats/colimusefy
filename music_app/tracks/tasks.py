from celery import shared_task
import spotipy
from .spotify_client import get_spotify_client


@shared_task
def fetch_album_data(album_id):
    sp = get_spotify_client()
    album = sp.album(album_id)
    total_duration_ms = sum(track['duration_ms'] for track in album['tracks']['items'])
    total_duration_min = total_duration_ms // 60000
    total_duration_sec = (total_duration_ms % 60000) // 1000
    return {
        'title': album['name'],
        'artists': [artist['name'] for artist in album['artists']],
        'album_image': album['images'][0]['url'],
        'duration': f"{total_duration_min}:{str(total_duration_sec).zfill(2)}"
    }