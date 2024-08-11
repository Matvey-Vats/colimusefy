from django.urls import path

from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('tracks/', views.track_list, name="track-list"),
    path('albums/', views.album_list, name="album-list"),
    path('artists/', views.artist_list, name="artist-list"),
    path('album/<slug:album_id>/', views.album_detail, name="album-detail"),
    path('artist/<slug:artist_id>/', views.artist_detail, name="artist-detail"),
]
