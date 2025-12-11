from django.urls import path
from .views import generate_music_from_text, music_page, generate_lyrics, save_track, save_track_publish, library_page, track_detail, edit_track_view, main_page, like_track, toggle_like, profile_view
from .views import edit_profile, register_view
urlpatterns = [
    path("generate-music-from-text/", generate_music_from_text, name="generate_music_from_text"),
    path('generate-lyrics/', generate_lyrics, name='generate_lyrics'),
    path("music/", music_page, name="music_page"),
    path('save-track/', save_track, name='save_track'),
    path('save-track/publish', save_track_publish, name='save_track_publish'),
    path("library/", library_page, name="library_page"),
    path('track/<int:pk>/', track_detail, name='track_detail'),
    path('track/<int:pk>/edit/', edit_track_view, name='edit_track'),
    path("main/", main_page, name="main_page"),
    path('like-track/<int:track_id>/', like_track, name='like_track'),
    path('toggle-like/<int:track_id>/', toggle_like, name='toggle_like'),
    path("profile/", profile_view, name="profile_view"),
    path("edit/profile/", edit_profile, name="edit_profile"),
    path('register/', register_view, name='register'),



]
