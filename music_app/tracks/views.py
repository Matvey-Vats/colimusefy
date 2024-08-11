from django.shortcuts import render
from .spotify_client import get_spotify_client
from django.conf import settings
from django.core.paginator import Paginator

from .tasks import fetch_album_data
from celery.result import AsyncResult
from .utils import process_albums_in_batches, fetch_results
import time


def get_artist_info(sp, artist_id):
    artist = sp.artist(artist_id)
    return {
        'name': artist['name'],
        'image': artist['images'][0]['url'] if artist.get('images') else ''
    }

def home(request):
    sp = get_spotify_client()
    
    # Получаем топ треков для жанра (например, поп)
    results = sp.search(q=f'year:{settings.CURRENT_YEAR}', type='track', limit=10)
    tracks = results['tracks']['items']
    
    # Собираем уникальные исполнители
    artist_ids = set(artist['id'] for track in tracks for artist in track['artists'])
    artists = [get_artist_info(sp, artist_id) for artist_id in artist_ids]
    
    # Сортируем исполнителей
    sorted_artists = sorted(artists, key=lambda x: x['name'])[:6]
    
    
    results = sp.search(q=f'year:{settings.CURRENT_YEAR}', type='album', limit=10)
    albums = results['albums']['items']
    
    # Извлекаем данные об альбомах
    popular_albums = [{
        'name': album['name'],
        'image': album['images'][0]['url'] if album.get('images') else '',
        'artist': album['artists'][0]['name']
    } for album in albums[:4]]
    
    return render(request, 'tracks/index.html', {'artists': sorted_artists, 'albums': popular_albums})    


def track_list(request):
    sp = get_spotify_client()
    
    result = sp.search(q=f'year:{settings.CURRENT_YEAR}', type='track', limit=50)
    tracks = result['tracks']['items']
    
    
    tracks_with_details = []
    for track in tracks:
        track_info = {
            'name': track['name'],
            'artists': [artist['name'] for artist in track['artists']],
            'album_image': track['album']['images'][0]['url'] if track['album']['images'] else None,
            'preview_url': track['preview_url'],  # URL для предварительного прослушивания
            'track_url': track['external_urls']['spotify']  # URL на Spotify для полного прослушивания
        }
        tracks_with_details.append(track_info)
        
    paginator = Paginator(tracks_with_details, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'tracks/tracks.html', {'tracks': page_obj,
                                                  'paginator': paginator,
                                                  'current_page': page_obj.number,})


# def album_list(request):
#     sp = get_spotify_client()
    
#     result = sp.search(q=f"year:{settings.CURRENT_YEAR}", type="album", limit=1)
#     albums_ids = [album['id'] for album in result['albums']['items']]
    
    # task_ids = [fetch_album_data.delay(album_id).id for album_id in albums_ids]
    
    # album = sp.album(album_id)
    
    # total_duration_ms = sum([track['duration_ms'] for track in album['tracks']['items']])
    # total_duration_min = total_duration_ms // 60000
    # total_duration_sec = (total_duration_ms % 60000) // 1000
    
    
    
    # albums_data = []
    # for task_id in task_ids:
    #     result = AsyncResult(task_id)
    #     try:
    #         # Использование get с таймаутом
    #         data = result.get(timeout=10)  # Укажите таймаут, если задачи могут занимать время
    #         albums_data.append(data)
    #     except Exception as e:
    #         # Обработка исключений, если задача завершилась с ошибкой
    #         print(f"Error retrieving result for task {task_id}: {e}")
        
    # return render(request, "tracks/albums.html", {"albums": albums_data})

def album_list(request):
    sp = get_spotify_client()
    start_time = time.time()
    
    result = sp.search(q=f"year:{settings.CURRENT_YEAR}", type="album", limit=50)
    albums_ids = [album['id'] for album in result['albums']['items']]
    print(f"Time to fetch album IDs: {time.time() - start_time} seconds")
    
    albums_data = []
    for album_id in albums_ids:
        start_time = time.time()
        album = sp.album(album_id)
        total_duration_ms = sum(track['duration_ms'] for track in album['tracks']['items'])
        total_duration_min = total_duration_ms // 60000
        total_duration_sec = (total_duration_ms % 60000) // 1000
        albums_data.append({
            'name': album['name'],
            'total_tracks': album['total_tracks'],
            'artists': [artist['name'] for artist in album['artists']],
            'album_image': album['images'][0]['url'],
            'duration': f"{total_duration_min}:{str(total_duration_sec).zfill(2)}"
        })
        print(f"Time to process album {album_id}: {time.time() - start_time} seconds")
        
        
    paginator = Paginator(albums_data, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, "tracks/albums.html", {"albums": page_obj,
                                                  'paginator': paginator,
                                                  'current_page': page_obj.number,})


# def album_list(request):
#     sp = get_spotify_client()
    
#     batch_size = 10  # Количество альбомов в одном пакете
#     all_albums_data = []
    
#     for task_ids in process_albums_in_batches(sp, settings.CURRENT_YEAR, batch_size):
#         albums_data = fetch_results(task_ids)
#         all_albums_data.extend(albums_data)
    
#     return render(request, "tracks/albums.html", {"albums": all_albums_data})



def artist_list(request):
    sp = get_spotify_client()
    
    result = sp.search(q=f'year:{settings.CURRENT_YEAR}', type='artist', limit=50)
    artists = result['artists']['items']
    
    atrists_data = []
    for artist in artists:
        artists_info = {
            'name': artist['name'],
            'image': artist['images'][0]['url'],
        } 
        atrists_data.append(artists_info)
        
    paginator = Paginator(atrists_data, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
        
    return render(request, "tracks/artists.html", {'artists': page_obj,
                                                   'paginator': paginator,
                                                   'current_page': page_obj.number,})