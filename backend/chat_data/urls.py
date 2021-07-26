from django.urls import path

from .views import rankedCommands, follow, followAge, new_rooms

urlpatterns = [
    path('rank/<user>/<command>/', rankedCommands, name='rank'),
    path('rank/<user>/', rankedCommands, name='rank'),
    path('follow/<int:user_id>/', follow, name='follow'),
    path('follow-age/<user>/', followAge, name='follow-age'),
    path('new_rooms/', new_rooms, name='new-rooms'),
]