from celery.result import AsyncResult
from .tasks import fetch_album_data
from itertools import islice

def get_albums(sp, year, limit=50):
    offset = 0
    while True:
        result = sp.search(q=f"year:{year}", type="album", limit=limit, offset=offset)
        albums = result['albums']['items']
        if not albums:
            break
        for album in albums:
            yield album
        offset += limit

def batch(iterable, batch_size):
    it = iter(iterable)
    while True:
        batch_items = list(islice(it, batch_size))
        if not batch_items:
            break
        yield batch_items

def process_albums_in_batches(sp, year, batch_size=10):
    for album_batch in batch(get_albums(sp, year), batch_size):
        task_ids = [fetch_album_data.delay(album['id']).id for album in album_batch]
        yield task_ids

def fetch_results(task_ids):
    results = []
    for task_id in task_ids:
        result = AsyncResult(task_id)
        try:
            data = result.get(timeout=10)  # Укажите таймаут, если задачи могут занимать время
            results.append(data)
        except Exception as e:
            print(f"Error retrieving result for task {task_id}: {e}")
    return results
