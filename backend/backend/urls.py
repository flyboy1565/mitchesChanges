from django.contrib import admin
from django.urls import path

from django.conf.urls import include
from rest_framework.routers import DefaultRouter
from chat_data.api.views import (
    StreamUsersViewSet, ChatMessageViewSet, BotTimeViewSet, 
    CommandUseViewSet, TextCommandsViewSet, FalseCommandsViewSet,
    BotTimeViewSet, FeatureRequestsViewSet
)


router = DefaultRouter()
router.register('users', StreamUsersViewSet, basename='users')
router.register('messages', ChatMessageViewSet, basename='messages')
router.register('command-usage', CommandUseViewSet, basename='commands-usage')
router.register('text-commands', TextCommandsViewSet, basename='text-commands')
router.register('false-commands', FalseCommandsViewSet, basename='false-commands')
router.register('bottime', BotTimeViewSet, basename='bottime')
router.register('feature-requests', FeatureRequestsViewSet, basename='feature-requests')


urlpatterns = [
    path('api/', include(router.urls)),
    path('api/', include('chat_data.urls')),
    path('admin/', admin.site.urls),
]