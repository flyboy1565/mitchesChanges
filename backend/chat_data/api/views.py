from django.shortcuts import get_list_or_404, get_object_or_404

from rest_framework.mixins import (
    CreateModelMixin, ListModelMixin, RetrieveModelMixin, UpdateModelMixin
)
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.decorators import action

from .serializers import *


class ChatMessageViewSet(GenericViewSet,  # generic view functionality
                    CreateModelMixin,  # handles POSTs
                    RetrieveModelMixin,  # handles GETs for 1 Company
                    UpdateModelMixin,  # handles PUTs and PATCHes
                    ListModelMixin):  # handles GETs for many Companies

    serializer_class = ChatMessageSerializer
    queryset = ChatMessages.objects.all()


class StreamUsersViewSet(GenericViewSet,  # generic view functionality
                    CreateModelMixin,  # handles POSTs
                    RetrieveModelMixin,  # handles GETs for 1 Company
                    UpdateModelMixin,  # handles PUTs and PATCHes
                    ListModelMixin):  # handles GETs for many Companies

    serializer_class = UsersSerializer
    queryset = StreamUsers.objects.all()


class UsersNameViewSet(GenericViewSet,  # generic view functionality
                    CreateModelMixin,  # handles POSTs
                    RetrieveModelMixin,  # handles GETs for 1 Company
                    UpdateModelMixin,  # handles PUTs and PATCHes
                    ListModelMixin):  # handles GETs for many Companies

    lookup_field = 'username'
    serializer_class = UsersSerializer
    queryset = StreamUsers.objects.all()


class CommandUseViewSet(GenericViewSet,  # generic view functionality
                    CreateModelMixin,  # handles POSTs
                    RetrieveModelMixin,  # handles GETs for 1 Company
                    UpdateModelMixin,  # handles PUTs and PATCHes
                    ListModelMixin):  # handles GETs for many Companies

    serializer_class = CommandUseSerializer
    queryset = CommandUse.objects.all()


class BotTimeViewSet(ModelViewSet):
    queryset = BotTime.objects.all().order_by('uptime')
    serializer_class = BotTimeSerializer

    @action(
        methods=['get'],
        detail=False,
        url_path='last',
        url_name='last',
    )
    def get_bottime(self, request, *args, **kwargs):
        last_pk = self.queryset.all().last().pk 
        self.kwargs.update(pk=last_pk)
        return self.retrieve(request, *args, **kwargs)


class TextCommandsViewSet(GenericViewSet,  # generic view functionality
                    CreateModelMixin,  # handles POSTs
                    RetrieveModelMixin,  # handles GETs for 1 Company
                    UpdateModelMixin,  # handles PUTs and PATCHes
                    ListModelMixin):  # handles GETs for many Companies

    serializer_class = TextCommandSerializer
    queryset = TextCommands.objects.all()


class FalseCommandsViewSet(GenericViewSet,  # generic view functionality
                    CreateModelMixin,  # handles POSTs
                    RetrieveModelMixin,  # handles GETs for 1 Company
                    UpdateModelMixin,  # handles PUTs and PATCHes
                    ListModelMixin):  # handles GETs for many Companies

    serializer_class = FalseCommandsSerializer
    queryset = FalseCommands.objects.all()


class FeatureRequestsViewSet(GenericViewSet,  # generic view functionality
                    CreateModelMixin,  # handles POSTs
                    RetrieveModelMixin,  # handles GETs for 1 Company
                    UpdateModelMixin,  # handles PUTs and PATCHes
                    ListModelMixin):  # handles GETs for many Companies

    serializer_class = FeatureRequestSerializer
    queryset = FeatureRequest.objects.all()