from django.shortcuts import render
from .spotify_client import get_spotify_client


# Create your views here.
def get_artist_info(sp, artist_id):
    artist = sp.artist(artist_id)
    return {
        'name': artist['name'],
        'image': artist['images'][0]['url'] if artist.get('images') else ''
    }

def home(request):
    sp = get_spotify_client()
    
    # Получаем топ треков для жанра (например, поп)
    results = sp.search(q='year:2024', type='track', limit=10)
    tracks = results['tracks']['items']
    
    # Собираем уникальные исполнители
    artist_ids = set(artist['id'] for track in tracks for artist in track['artists'])
    artists = [get_artist_info(sp, artist_id) for artist_id in artist_ids]
    
    # Сортируем исполнителей
    sorted_artists = sorted(artists, key=lambda x: x['name'])[:6]
    
    
    results = sp.search(q='year:2024', type='album', limit=10)
    albums = results['albums']['items']
    
    # Извлекаем данные об альбомах
    popular_albums = [{
        'name': album['name'],
        'image': album['images'][0]['url'] if album.get('images') else '',
        'artist': album['artists'][0]['name']
    } for album in albums[:4]]
    
    return render(request, 'tracks/index.html', {'artists': sorted_artists, 'albums': popular_albums})    