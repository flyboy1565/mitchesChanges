from django.urls import path

from .views import rankedCommands

urlpatterns = [
    path('rank/<user>/<command>/', rankedCommands, name='rank'),
    path('rank/<user>/', rankedCommands, name='rank'),
]