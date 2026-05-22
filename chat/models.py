from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class ChatRoom(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    participants = models.ManyToManyField(
        User,
        blank=True,
        related_name='rooms',
        verbose_name='Участники'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Чат-комната'
        verbose_name_plural = 'Чат-комнаты'

class ChatFile(models.Model):
    file = models.FileField(upload_to='chat_files/%Y/%m/%d/')
    original_name = models.CharField(max_length=255)
    room_name = models.CharField(max_length=255)
    uploaded_by = models.CharField(max_length=150)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    size = models.IntegerField()

    def __str__(self):
        return self.original_name

class Message(models.Model):
    TYPE_CHOICES = [
        ('text', 'Text'),
        ('file', 'File'),
    ]
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    username = models.CharField(max_length=150)
    message_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='text')
    content = models.TextField(blank=True, null=True)
    file_url = models.URLField(blank=True, null=True)
    file_name = models.CharField(max_length=255, blank=True, null=True)
    file_size = models.IntegerField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    bio = models.TextField(max_length=1000, blank=True, verbose_name="Описание")
    photo = models.ImageField(upload_to='profiles/', blank=True, null=True,verbose_name='Фото профиля')

    def get_absolute_url(self):
        return reverse('profile', kwargs={'username': self.user.username})