from django.contrib.auth.models import User
from .models import Profile
from django.contrib.auth.forms import *
from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions

class RegistrationForm(UserCreationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-input'}))
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    password2 = forms.CharField(label='Повтор пароля', widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')

class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-input'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}))

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'photo']

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')

        if not photo:
            return photo

        max_size = 10 * 1024 * 1024
        if photo.size > max_size:
             raise ValidationError("Размер файла не должен превышать 10 МБ.")

        width, height = get_image_dimensions(photo)

        if not width or not height:
            raise ValidationError("Не удалось распознать формат или размеры изображения.")

        if width < 200 or height < 200:
            raise ValidationError(
                f"Изображение слишком маленькое ({width}x{height}). Минимальный размер: 200x200 пикселей.")

        if width > 1000 or height > 1000:
            raise ValidationError(
                f"Изображение слишком большое ({width}x{height}). Максимальный размер: 1000x1000 пикселей.")

        return photo