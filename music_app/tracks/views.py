from django.shortcuts import render
from .spotify_client import get_spotify_client
from django.conf import settings
from django.core.paginator import Paginator
from django.views.decorators.cache import cache_page


from .tasks import get_album_data, get_popular_items
from celery.result import AsyncResult
import time


def get_artist_info(sp, artist_id):
    artist = sp.artist(artist_id)
    return {
        'id': artist['id'],
        'name': artist['name'],
        'image': artist['images'][0]['url'] if artist.get('images') else ''
    }

# @cache_page(60 * 15)
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
        'id': album['id'],
        'name': album['name'],
        'image': album['images'][0]['url'] if album.get('images') else '',
        'artist': album['artists'][0]['name']
    } for album in albums[:4]]
    
    return render(request, 'tracks/index.html', {'artists': sorted_artists, 'albums': popular_albums})    

# @cache_page(60 * 15)
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


# @cache_page(60 * 15)
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
            'id': album['id'],
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


# @cache_page(60 * 15)
def artist_list(request):
    sp = get_spotify_client()
    
    result = sp.search(q=f'year:{settings.CURRENT_YEAR}', type='artist', limit=50)
    artists = result['artists']['items']
    
    atrists_data = []
    for artist in artists:
        artists_info = {
            'id': artist['id'],
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
    

def album_detail(request, album_id):

    result = get_album_data(album_id)
    
    tracks = result['tracks']['items']
    
    paginator = Paginator(tracks, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'tracks/album_detail.html', {"album": result,
                                                        'tracks': page_obj,
                                                        'paginator': paginator,
                                                        'current_page': page_obj.number,})
    

def artist_detail(request, artist_id):
    sp = get_spotify_client()
    
    result = sp.artist(artist_id)
    
    albums = sp.artist_albums(artist_id=artist_id, album_type='album', limit=50)
    
    
    albums_data = []

    for album in albums['items']:  # 'items' - это список альбомов
        album_info = {
            'id': album['id'],
            'image': album['images'][0]['url'] if album['images'] else None,  # Проверка на наличие изображений
            'name': album['name'],
        }
        albums_data.append(album_info)
    
    paginator = Paginator(albums_data, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'tracks/artist_detail.html', {'artist': result,
                                                         'albums': page_obj,
                                                         'paginator': paginator,
                                                         'current_page': page_obj.number,})

# def search(request):
#     sp = get_spotify_client()
#     query = request.GET.get('query')
    
#     def perform_search(search_query):
#         tracks = sp.search(q=search_query, type='track', limit=5)['tracks']['items']
#         albums = sp.search(q=search_query, type='album', limit=5)['albums']['items']
#         artists = sp.search(q=search_query, type='artist', limit=5)['artists']['items']
        
#         return {
#             'tracks': tracks,
#             'albums': albums,
#             'artists': artists,
#         }
    
#     if not query:
#         results = perform_search(f'year:{settings.CURRENT_YEAR}')
#     else:
#         results = perform_search(query)
    
#     return render(request, "tracks/search.html", {'results': results})

    

def search(request):
    query = request.GET.get('query')
    
    if not query:
        # Если запрос пуст, загружаем популярные треки, альбомы и исполнителей.
        results = get_popular_items()
    else:
        # Иначе выполняем поиск по запросу.
        sp = get_spotify_client()
        results = {
            'tracks': sp.search(q=query, type='track', limit=5)['tracks']['items'],
            'albums': sp.search(q=query, type='album', limit=5)['albums']['items'],
            'artists': sp.search(q=query, type='artist', limit=5)['artists']['items'],
        }
    
    return render(request, "tracks/search.html", {'results': results})