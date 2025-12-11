import requests
from mutagen.mp3 import MP3
from django.urls import reverse
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.files.base import ContentFile



# Расширяем стандартного пользователя
class User(AbstractUser):
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


def download_file(url):
    response = requests.get(url)
    if response.status_code == 200:
        return ContentFile(response.content)
    return None
# Музыкальные треки
class Track(models.Model):
    GENRE_CHOICES = [
        ('pop', 'Поп'),
        ('rock', 'Рок'),
        ('electronic', 'Электронная'),
        ('hiphop', 'Хип-хоп'),
    ]
    MOOD_CHOICES = [
        ('energetic', 'Энергичное'),
        ('calm', 'Спокойное'),
        ('dreamy', 'Мечтательное'),
        ('sad', 'Грустное'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tracks')
    title = models.CharField(max_length=255)
    genre = models.CharField(max_length=100, choices=GENRE_CHOICES)
    mood = models.CharField(max_length=100, choices=MOOD_CHOICES)
    topic = models.CharField(max_length=255)
    lyrics = models.TextField()
    audio_file_url = models.URLField()
    audio_file = models.FileField(upload_to='tracks/', blank=True, null=True)
    image_url = models.URLField()
    listens_count = models.PositiveIntegerField(default=0)
    likes_count = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    duration = models.PositiveIntegerField(null=True, blank=True)
    liked_by = models.ManyToManyField(User, related_name='liked_tracks', blank=True)

    def save(self, *args, **kwargs):
        if self.audio_file_url and not self.audio_file:
            file_content = download_file(self.audio_file_url)
            if file_content:
                filename = f"{self.title.replace(' ', '_')}.mp3"
                self.audio_file.save(filename, file_content, save=False)

                try:
                    self.audio_file.seek(0)  # Перематываем в начало
                    audio = MP3(self.audio_file)
                    self.duration = int(audio.info.length)
                except Exception as e:
                    print("Не удалось определить длительность: {e}")
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('track_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.title

# Лайки
class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'track')

# Библиотека (сохранённые треки)
class LibraryItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'track')


class GenerationTask(models.Model):
    STATUS_CHOICES = [
        ('text_generation', 'Генерация текста'),
        ('text_ready', 'Текст сгенерирован'),
        ('melody_generation', 'Создание мелодии'),
        ('melody_ready', 'Мелодия готова'),
        ('error', 'Ошибка'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generation_tasks')
    genre = models.CharField(max_length=100)
    mood = models.CharField(max_length=100)
    theme = models.CharField(max_length=255)
    lyrics = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='text_generation')
    track_stream_url = models.URLField(blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"Задача для {self.user.username} [{self.get_status_display()}]"