from django import forms
from .models import Track

class TrackEditForm(forms.ModelForm):
    class Meta:
        model = Track
        fields = ['title', 'genre', 'mood', 'topic', 'lyrics', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full bg-gray-900/50 rounded-lg p-3 text-gray-300 border border-gray-700/30 focus:ring-2 focus:ring-gray-500 outline-none'
            }),
            'genre': forms.Select(attrs={
                'class': 'w-full bg-gray-900/50 rounded-lg p-3 text-gray-300 border border-gray-700/30 focus:ring-2 focus:ring-gray-500 outline-none'
            }),
            'mood': forms.Select(attrs={
                'class': 'w-full bg-gray-900/50 rounded-lg p-3 text-gray-300 border border-gray-700/30 focus:ring-2 focus:ring-gray-500 outline-none'
            }),
            'topic': forms.TextInput(attrs={
                'class': 'w-full bg-gray-900/50 rounded-lg p-3 text-gray-300 border border-gray-700/30 focus:ring-2 focus:ring-gray-500 outline-none'
            }),
            'lyrics': forms.Textarea(attrs={
                'class': 'w-full bg-gray-900/50 rounded-lg p-3 text-gray-300 border border-gray-700/30 focus:ring-2 focus:ring-gray-500 outline-none',
                'rows': 6
            }),
            'is_published': forms.CheckboxInput(attrs={
                'class': 'mr-2 align-middle'
            }),
        }


from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'w-full bg-gray-800/50 border border-gray-700/30 rounded-lg px-4 py-2 text-gray-200 focus:outline-none focus:border-gray-500 transition-colors',
        'placeholder': 'Введите email',
    }))
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'w-full bg-gray-800/50 border border-gray-700/30 rounded-lg px-4 py-2 text-gray-200 focus:outline-none focus:border-gray-500 transition-colors',
        'placeholder': 'Введите имя',
    }))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'w-full bg-gray-800/50 border border-gray-700/30 rounded-lg px-4 py-2 text-gray-200 focus:outline-none focus:border-gray-500 transition-colors',
        'placeholder': 'Введите пароль',
    }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'w-full bg-gray-800/50 border border-gray-700/30 rounded-lg px-4 py-2 text-gray-200 focus:outline-none focus:border-gray-500 transition-colors',
        'placeholder': 'Повторите пароль',
    }))

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
