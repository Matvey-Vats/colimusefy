import redis
from django.conf import settings
from celery import shared_task
from .spotify_client import get_spotify_client

import json

# Настройка подключения к Redis
redis_client = redis.Redis(host="redis", port=6379, db=0)

@shared_task
def fetch_and_cache_album_data(album_id):
    sp = get_spotify_client()
    album = sp.album(album_id)
    
    # Формирование данных альбома
    album_data = {
        'name': album['name'],
        'artist': ', '.join([artist['name'] for artist in album['artists']]),
        'image_url': album['images'][0]['url'],
        'total_tracks': album['total_tracks'],
        'tracks': [{'name': track['name'], 'duration': track['duration_ms']} for track in album['tracks']['items']],
    }
    
    # Кэширование данных в Redis
    redis_key = f"album_data:{album_id}"
    redis_client.set(redis_key, json.dumps(album_data), ex=3600)  # Кэширование на 1 час

    return album_data

def get_album_data(album_id):
    redis_key = f"album_data:{album_id}"
    
    # Попытка получить данные из кэша Redis
    cached_data = redis_client.get(redis_key)
    if cached_data:
        return json.loads(cached_data)
    
    # Если данных нет в кэше, инициировать задачу для их получения
    result = fetch_and_cache_album_data.delay(album_id)
    return result.get()


@shared_task
def fetch_and_cache_album_data(album_id):
    sp = get_spotify_client()
    album = sp.album(album_id)
    
    # Формирование данных альбома
    album_data = {
        'name': album['name'],
        'artist': ', '.join([artist['name'] for artist in album['artists']]),
        'image_url': album['images'][0]['url'],
        'total_tracks': album['total_tracks'],
        'tracks': [{'name': track['name'], 'duration': track['duration_ms']} for track in album['tracks']['items']],
    }
    
    # Кэширование данных в Redis
    redis_key = f"album_data:{album_id}"
    redis_client.set(redis_key, json.dumps(album_data), ex=3600)  # Кэширование на 1 час

    return album_data

def get_album_data(album_id):
    redis_key = f"album_data:{album_id}"
    
    # Попытка получить данные из кэша Redis
    cached_data = redis_client.get(redis_key)
    if cached_data:
        return json.loads(cached_data)
    
    # Если данных нет в кэше, инициировать задачу для их получения
    result = fetch_and_cache_album_data.delay(album_id)
    return result.get()




@shared_task
def fetch_popular_items():
    sp = get_spotify_client()
    year = settings.CURRENT_YEAR
    
    popular_tracks = sp.search(q=f'year:{year}', type='track', limit=5)['tracks']['items']
    popular_albums = sp.search(q=f'year:{year}', type='album', limit=5)['albums']['items']
    popular_artists = sp.search(q=f'year:{year}', type='artist', limit=5)['artists']['items']
    
    data = {
        'tracks': popular_tracks,
        'albums': popular_albums,
        'artists': popular_artists,
    }
    
    # Кэширование данных
    redis_key = f"popular_items:{year}"
    redis_client.set(redis_key, json.dumps(data), ex=3600)
    
    return data

def get_popular_items():
    year = settings.CURRENT_YEAR
    redis_key = f"popular_items:{year}"
    
    # Попытка получить данные из кэша Redis
    cached_data = redis_client.get(redis_key)
    if cached_data:
        return json.loads(cached_data)
    
    # Если данных нет в кэше, инициировать задачу для их получения
    result = fetch_popular_items.delay()
    return result.get()