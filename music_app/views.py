import requests
from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import time
import openai
import json


@csrf_exempt
def generate_lyrics(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        genre = data.get('genre')
        mood = data.get('mood')
        theme = data.get('theme')

        if not (genre and mood and theme):
            return JsonResponse({'error': 'All fields are required'}, status=400)

        openai.api_key = settings.OPENAI_API_KEY

        prompt = f"""Сгенерируй текст для песни на казахском. 
Жанр: {genre}
Настроение: {mood}
Тема: {theme}

Текст песни:"""

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4-0125-preview",
                messages=[
                    {"role": "system", "content": "Ты креативный генератор песенных текстов."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.8
            )
            lyrics = response.choices[0].message["content"].strip()

            return JsonResponse({'lyrics': lyrics})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)


def music_page(request):
    return render(request, "generate_music_page.html")

@csrf_exempt
def generate_music_from_text(request):
    """ Генерация музыки на основе введённого пользователем текста """
    if request.method == "POST":
        lyrics = request.POST.get("lyrics", "")
        genre = request.POST.get("genre", "")
        mood = request.POST.get("mood", "")

        if not lyrics:
            return JsonResponse({"success": False, "error": "Введите текст песни."})

        url = "https://apibox.erweima.ai/api/v1/generate"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.SUNO_API_KEY}"
        }
        payload = {
            "prompt": lyrics,
            "style": genre,
            "title": mood,
            "customMode": True,
            "instrumental": False,
            "model": "V3_5",
            "callBackUrl": "https://api.example.com/callback"
        }

        response = requests.post(url, headers=headers, json=payload)
        response_data = response.json()
        print("API Response:", response_data)

        if "data" not in response_data or response_data["code"] != 200:
            return JsonResponse({"success": False, "error": "Ошибка генерации музыки. Проверь API."})

        task_id = response_data["data"]["taskId"]

        # Ждём, пока музыка будет готова
        check_status_url = f"https://apibox.erweima.ai/api/v1/generate/record-info?taskId={task_id}"
        for _ in range(10):  # Проверяем 10 раз с интервалом в 5 секунд
            status_response = requests.get(check_status_url, headers=headers).json()
            print("API Response:", status_response)  # Отладка

            if "data" in status_response and "response" in status_response["data"] and status_response["data"]["response"]:
                suno_data = status_response["data"]["response"].get("sunoData", [])

                if suno_data:
                    # Берём первый вариант трека
                    track = suno_data[0]
                    return JsonResponse({
                        "success": True,
                        "stream_url": track.get("streamAudioUrl", ""),
                        "image_url": track.get("imageUrl", "")
                    })

            time.sleep(10)  # Ждём 5 секунд перед повторной проверкой

        return JsonResponse({"success": False, "error": "Музыка ещё не готова. Попробуйте позже."})

    return JsonResponse({"success": False, "error": "Некорректный метод запроса."})

from django.contrib.auth.decorators import login_required
from .models import Track

@csrf_exempt
@login_required
def save_track(request):
    if request.method == 'POST':
        user = request.user
        data = json.loads(request.body)
        title = data.get('title')
        genre = data.get('genre')
        mood = data.get('mood')
        topic = data.get('topic')
        lyrics = data.get('lyrics')
        audio_url = data.get('audio_url')
        image_url = data.get('image_url')

        if not all([title, genre, mood, topic, lyrics, audio_url, image_url]):
            return JsonResponse({'error': 'Все поля должны быть заполнены'}, status=400)

        track = Track.objects.create(
            user=user,
            title=title,
            genre=genre,
            mood=mood,
            topic=topic,
            lyrics=lyrics,
            audio_file_url=audio_url,
            image_url=image_url,
            is_published=False
        )

        return JsonResponse({'success': True, 'track_id': track.id})

    return JsonResponse({'error': 'Неверный метод'}, status=405)

@csrf_exempt
@login_required
def save_track_publish(request):
    if request.method == 'POST':
        user = request.user
        data = json.loads(request.body)
        title = data.get('title')
        genre = data.get('genre')
        mood = data.get('mood')
        topic = data.get('topic')
        lyrics = data.get('lyrics')
        audio_url = data.get('audio_url')
        image_url = data.get('image_url')

        if not all([title, genre, mood, topic, lyrics, audio_url, image_url]):
            return JsonResponse({'error': 'Все поля должны быть заполнены'}, status=400)

        track = Track.objects.create(
            user=user,
            title=title,
            genre=genre,
            mood=mood,
            topic=topic,
            lyrics=lyrics,
            audio_file_url=audio_url,
            image_url=image_url,
            is_published=True
        )

        return JsonResponse({'success': True, 'track_id': track.id})

    return JsonResponse({'error': 'Неверный метод'}, status=405)


@login_required
def library_page(request):
    user_tracks = Track.objects.filter(user=request.user)
    return render(request, 'library_page.html', {'tracks': user_tracks})

def track_detail(request, pk):
    track = get_object_or_404(Track, pk=pk)
    track.listens_count += 1
    track.save()
    return render(request, 'track_detail.html', {
        'track': track,
        'title': track.title,
        'artist': track.user.username,
        'genre': track.genre,
        'image_url': track.image_url,
        'audio_url': track.audio_file.url,
        'likes_count': track.likes_count,
        'listens_count': track.listens_count,
        'release_date': track.created_at.strftime('%d.%m.%Y'),
        'lyrics': track.lyrics.split('\n')  # делим текст на строки для красивого отображения
    })


@login_required
def main_page(request):
    tracks = Track.objects.filter(is_published=True)
    return render(request, 'main_page.html', {'tracks': tracks})


from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from .models import Track
from .forms import TrackEditForm
@login_required
def edit_track_view(request, pk):
    track = get_object_or_404(Track, pk=pk, user=request.user)

    if request.method == 'POST':
        form = TrackEditForm(request.POST, instance=track)
        if form.is_valid():
            form.save()
            return redirect('library_page')
    else:
        form = TrackEditForm(instance=track)

    return render(request, 'edit_track.html', {'form': form, 'track': track})


@csrf_exempt
def like_track(request, track_id):
    if request.method == 'POST':
        try:
            track = Track.objects.get(pk=track_id)
            track.likes_count += 1
            track.save()
            return JsonResponse({'success': True, 'likes_count': track.likes_count})
        except Track.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Трек не найден.'})
    return JsonResponse({'success': False, 'error': 'Неверный метод.'})

@login_required
def toggle_like(request, track_id):
    track = Track.objects.get(id=track_id)
    user = request.user

    if user in track.liked_by.all():
        track.liked_by.remove(user)
        liked = False
    else:
        track.liked_by.add(user)
        liked = True

    track.likes_count = track.liked_by.count()
    track.save()

    return JsonResponse({'liked': liked, 'likes_count': track.likes_count})

@login_required
def profile_view(request):
    user = request.user
    user_tracks = Track.objects.filter(user=user)
    total_tracks = user_tracks.count()
    published_tracks = user_tracks.filter(is_published=True).count()
    draft_tracks = user_tracks.filter(is_published=False).count()
    liked_tracks = user.liked_tracks.all()

    return render(request, 'profile_page.html', {
        'user': user,
        'total_tracks': total_tracks,
        'published_tracks': published_tracks,
        'draft_tracks': draft_tracks,
        'liked_tracks': liked_tracks
    })

from django.contrib import messages
from django import forms
from django.contrib.auth.models import User
# Форма для редактирования профиля
class ProfileEditForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={
        'class': 'w-full bg-gray-800/50 border border-gray-700/30 rounded-lg px-4 py-2 text-gray-200 focus:outline-none focus:border-gray-500 transition-colors',
        'placeholder': 'Имя'
    }))
    last_name = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={
        'class': 'w-full bg-gray-800/50 border border-gray-700/30 rounded-lg px-4 py-2 text-gray-200 focus:outline-none focus:border-gray-500 transition-colors',
        'placeholder': 'Фамилия'
    }))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'w-full bg-gray-800/50 border border-gray-700/30 rounded-lg px-4 py-2 text-gray-200 focus:outline-none focus:border-gray-500 transition-colors',
        'placeholder': 'Email'
    }))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлён!')
            return redirect('profile_view')
    else:
        form = ProfileEditForm(instance=request.user)

    return render(request, 'edit_profile.html', {'form': form})


from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegistrationForm
def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})




