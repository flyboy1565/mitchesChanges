from rest_framework.serializers import ModelSerializer, HyperlinkedModelSerializer

from chat_data.models import *


class UsersSerializer(ModelSerializer):
    class Meta:
            model = StreamUsers
            fields = '__all__'


class ChatMessageSerializer(ModelSerializer):
    class Meta:
        model = ChatMessages
        fields = '__all__'


class ChatRoomsSerializer(ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = '__all__'


class CommandUseSerializer(ModelSerializer):
    class Meta:
        model = CommandUse
        fields = '__all__'


class TextCommandSerializer(ModelSerializer):
    class Meta:
        model = TextCommands
        fields = '__all__'


class BotTimeSerializer(ModelSerializer):
    class Meta:
        model = BotTime
        fields = '__all__'


class FalseCommandsSerializer(ModelSerializer):
    class Meta:
        model = FalseCommands
        fields = '__all__'


class FeatureRequestSerializer(ModelSerializer):
    class Meta: 
        model = FeatureRequest
        fields = '__all__'


class RoomsToMonitorSerializer(ModelSerializer):
    class Meta: 
        model = RoomsToMonitor
        fields = ('name','active')
        # lookup_field = 'pk'