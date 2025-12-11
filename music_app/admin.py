from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, Track, Like, LibraryItem, GenerationTask

# Кастомизация админки для User
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'created_at', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-created_at',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'avatar')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    readonly_fields = ('date_joined', 'last_login', 'created_at')

# Отображение превьюшки изображения в админке для треков
class TrackAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'genre', 'mood', 'listens_count', 'likes_count', 'is_published', 'created_at', 'thumbnail')
    list_filter = ('genre', 'mood', 'is_published')
    search_fields = ('title', 'lyrics', 'topic', 'user__username')
    ordering = ('-created_at',)
    readonly_fields = ('listens_count', 'likes_count', 'created_at', 'thumbnail')
    fields = ('user', 'title', 'genre', 'mood', 'topic', 'lyrics', 'audio_file_url', 'audio_file', 'image_url', 'duration', 'thumbnail', 'listens_count', 'likes_count', 'is_published', 'created_at')

    def thumbnail(self, obj):
        if obj.image_url:
            return format_html('<img src="{}" width="80" height="80" style="object-fit:cover; border-radius:8px;" />', obj.image_url)
        return "-"
    thumbnail.short_description = 'Preview'

class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'track', 'created_at')
    search_fields = ('user__username', 'track__title')
    ordering = ('-created_at',)

class LibraryItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'track', 'saved_at')
    search_fields = ('user__username', 'track__title')
    ordering = ('-saved_at',)

# Регистрация моделей в админке
admin.site.register(Track, TrackAdmin)
admin.site.register(Like, LikeAdmin)
admin.site.register(LibraryItem, LibraryItemAdmin)


@admin.register(GenerationTask)
class GenerationTaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'genre', 'mood', 'theme', 'status', 'created_at', 'preview_image', 'has_audio')
    list_filter = ('status', 'genre', 'mood')
    search_fields = ('user__username', 'theme', 'lyrics')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'preview_image', 'track_stream_url', 'image_url', 'lyrics')

    def preview_image(self, obj):
        if obj.image_url:
            return format_html('<img src="{}" width="80" height="80" style="object-fit:cover; border-radius:8px;" />', obj.image_url)
        return "-"
    preview_image.short_description = 'Обложка'

    def has_audio(self, obj):
        return bool(obj.track_stream_url)
    has_audio.boolean = True
    has_audio.short_description = 'Есть аудио'
