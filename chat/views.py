import os
from traceback import print_tb
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse,HttpResponse
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.utils.text import get_valid_filename
from .forms import ProfileForm
from .models import ChatRoom, ChatFile, Message, Profile
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from .forms import *
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import ChatRoom

def menu_creator(request):
    menu = [
        {'title': "Главная страница", 'url_name': 'index'},
        {'title': "Мои комнаты", 'url_name': 'my_rooms'},
    ]
    if request.user.is_staff or request.user.is_superuser:
        menu.append({'title': "Админ-панель", 'url_name': 'admin:index'})
    return(menu)

@login_required(login_url='/login/')
def index(request):
    query = request.GET.get('q', '')
    rooms_list = Room.objects.all().order_by('-created_at')
    if query:
        rooms_list = rooms_list.filter(name__icontains=query)
    paginator = Paginator(rooms_list, 10)
    page = request.GET.get('page')
    rooms = paginator.get_page(page)
    return render(request, 'chat/index.html', {'rooms': rooms, 'query': query})

@login_required(login_url='/login/')
def my_rooms(request):
    query = request.GET.get('q', '')
    rooms_list = request.user.rooms.all().order_by('-created_at')
    if query:
        rooms_list = rooms_list.filter(name__icontains=query)
    paginator = Paginator(rooms_list, 10)
    page = request.GET.get('page')
    rooms = paginator.get_page(page)
    return render(request, 'chat/my_rooms.html', {'rooms': rooms, 'query': query})

@login_required(login_url='/login/')
def create_room(request):
    if request.method == 'POST':
        room_name = request.POST.get('room_name')
        if room_name:
            safe_name = get_valid_filename(room_name)
            if safe_name:
                room, created = ChatRoom.objects.get_or_create(name=safe_name)
                room.participants.add(request.user)
                return redirect('room', room_name=safe_name)
    return redirect('index')

@login_required(login_url='/login/')
def room(request, room_name):
    room = get_object_or_404(ChatRoom, name=room_name)

    if request.user not in room.participants.all():
        room.participants.add(request.user)

    context = {
        'room_name': room_name,
        'menu': menu_creator(request),
        'username': request.user.username,
        'room': room,
    }
    return render(request, 'chat/room.html', context=context)

@login_required(login_url='/login/')
def leave_room(request, room_name):
    room = get_object_or_404(ChatRoom, name=room_name)
    room.participants.remove(request.user)
    messages.success(request, f'Вы покинули комнату "{room_name}"')
    return redirect('my_rooms')

class RegistrationUser(CreateView):
    form_class = RegistrationForm
    template_name = 'chat/register.html'
    success_url = reverse_lazy('index')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Регистрация'
        return context

    def form_valid(self, form):
        user = form.save()
        Profile.objects.create(user=user)
        login(self.request, user)
        return redirect('index')

class LoginUser(LoginView):
    form_class = LoginForm
    template_name = 'chat/login.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Авторизация'
        return context

def logout_user(request):
    logout(request)
    return redirect('login')

@require_http_methods(["POST"])
@login_required(login_url='/login/')
def upload_file(request, room_name):
    username = request.user.username

    if 'file' not in request.FILES:
        return JsonResponse({'error': 'Файл не передан'}, status=400)

    uploaded_file = request.FILES['file']

    if uploaded_file.size > 10 * 1024 * 1024:
        return JsonResponse({'error': 'Файл не должен превышать 10 МБ'}, status=400)

    safe_filename = get_valid_filename(uploaded_file.name)
    safe_room = get_valid_filename(room_name)
    if not safe_filename or not safe_room:
        return JsonResponse({'error': 'Некорректное имя файла или комнаты'}, status=400)

    relative_path = os.path.join('chat_files', safe_room, safe_filename)
    full_path = default_storage.save(relative_path, uploaded_file)
    file_url = request.build_absolute_uri(default_storage.url(full_path))

    ChatFile.objects.create(
        file=full_path,
        original_name=uploaded_file.name,
        room_name=safe_room,
        uploaded_by=username,
        size=uploaded_file.size
    )

    return JsonResponse({
        'url': file_url,
        'name': safe_filename,
        'size': uploaded_file.size,
    })

@login_required(login_url='/login/')
def profile(request, username):
    user_object = get_object_or_404(User, username=username)
    return render(request, 'chat/profile.html', {'profile_user': user_object,'menu': menu_creator(request)})

def pageNotFound(request,exception):
    return render(request, 'chat/404.html', status=404)

@login_required(login_url='/login/')
def index(request):
    query = request.GET.get('q', '')
    rooms_list = ChatRoom.objects.all().order_by('-created_at')

    if query:
        rooms_list = rooms_list.filter(name__icontains=query)

    paginator = Paginator(rooms_list, 10)
    page_number = request.GET.get('page')
    rooms = paginator.get_page(page_number)

    context = {
        'rooms': rooms,
        'query': query,
    }
    return render(request, 'chat/index.html', context)

@login_required
def my_rooms(request):
    query = request.GET.get('q', '')
    rooms_list = request.user.rooms.all().order_by('-created_at')

    if query:
        rooms_list = rooms_list.filter(name__icontains=query)

    paginator = Paginator(rooms_list, 10)
    page_number = request.GET.get('page')
    rooms = paginator.get_page(page_number)

    context = {
        'rooms': rooms,
        'query': query,
    }
    return render(request, 'chat/my_rooms.html', context)

@login_required
def edit_profile(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль обновлён!')
            return redirect('edit_profile')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'chat/edit_profile.html', {'form': form})
