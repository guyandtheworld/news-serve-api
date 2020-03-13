from django.contrib.auth.models import User
from rest_framework.serializers import ModelSerializer
from django.contrib.auth.forms import UserCreationForm
from .models.entity import Entity, Alias
from .models.users import DashUser


class EntitySerializer(ModelSerializer):

    class Meta:
        model = Entity
        exclude = ["uuid"]


class AliasSerializer(ModelSerializer):
    class Meta:
        model = Alias
        exclude = ["uuid"]


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username',
                  'email', 'password')


class DashUserSerializer(ModelSerializer):
    class Meta:
        model = DashUser
        fields = ["user", "status", "clientID", "defaultScenario"]
