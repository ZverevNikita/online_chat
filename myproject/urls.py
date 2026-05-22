from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from chat.views import *
from django.views.static import serve


urlpatterns = [
    path('', RedirectView.as_view(url='/chat/', permanent=False)),
    path('admin/', admin.site.urls),
    path('chat/', include('chat.urls')),
    path('register/', RegistrationUser.as_view(), name='register'),
    path('login/', LoginUser.as_view(), name='login'),
    path('logout/', logout_user, name='logout'),
    path('profile/view/<str:username>/', profile, name='profile'),
    path('profile/edit/', edit_profile, name='edit_profile'),
]

urlpatterns += [
    re_path(
        r'^media/(?P<path>.*)$',
        serve,
        {'document_root': settings.MEDIA_ROOT},
    ),
]

handler404 = pageNotFound