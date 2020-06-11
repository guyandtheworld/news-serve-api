from django.contrib.auth.models import User
from rest_framework.serializers import ModelSerializer

from apis.models.entity import Entity
from apis.models.scenario import Scenario, Bucket
from apis.models.users import DashUser


class EntitySerializer(ModelSerializer):
    class Meta:
        model = Entity
        fields = "__all__"


class ScenarioSerializer(ModelSerializer):
    class Meta:
        model = Scenario
        fields = "__all__"


class BucketSerializer(ModelSerializer):
    class Meta:
        model = Bucket
        fields = "__all__"


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name"]


class DashUserSerializer(ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = DashUser
        fields = ["uuid", "user", "role"]
