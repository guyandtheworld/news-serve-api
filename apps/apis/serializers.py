from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.core import exceptions
from django.core.validators import validate_email

from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from .models.scenario import Scenario, Bucket, Keywords
from .models.users import DashUser, Client, UserScenario
from .models.entity import Entity


def validateEmail(email):
    try:
        validate_email(email)
    except exceptions.ValidationError:
        return False
    return True


class ScenarioSerializer(ModelSerializer):
    class Meta:
        model = Scenario
        fields = "__all__"


class ScenarioListSerializer(ModelSerializer):
    class Meta:
        model = UserScenario
        fields = "__all__"


class BucketSerializer(ModelSerializer):
    class Meta:
        model = Bucket
        fields = "__all__"


class ClientSerializer(ModelSerializer):
    class Meta:
        model = Client
        fields = "__all__"


class UserScenarioSerializer(ModelSerializer):
    class Meta:
        model = UserScenario
        fields = "__all__"


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password')


class DashUserSerializer(ModelSerializer):
    class Meta:
        model = DashUser
        fields = ["status", "clientID", "defaultScenario"]


class KeywordSerializer(ModelSerializer):
    keywords = serializers.ListField(child=serializers.CharField(max_length=100))

    class Meta:
        model = Keywords
        fields = ["keywords", "scenarioID"]


class EntityDetailSerializer(ModelSerializer):
    class Meta:
        model = Entity
        fields = ["uuid", "name", "typeID", "keywords"]


class BucketDetailSerializer(ModelSerializer):
    class Meta:
        model = Bucket
        fields = ["uuid", "name", "keywords"]


class ScenarioDetailSerializer(ModelSerializer):
    entity = EntityDetailSerializer(many=True)
    bucket = BucketDetailSerializer(many=True)
    class Meta:
        model = Scenario
        fields = ["uuid", "name", "trackingDays", "entity", "bucket"]

class AuthCustomTokenSerializer(serializers.Serializer):
    """
    used for logging in with email
    """
    email_or_username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        email_or_username = attrs.get('email_or_username')
        password = attrs.get('password')

        if email_or_username and password:
            # Check if user sent email
            if validateEmail(email_or_username):
                user_request = get_object_or_404(
                    User,
                    email=email_or_username,
                )

                email_or_username = user_request.username

            user = authenticate(username=email_or_username, password=password)

            if user:
                if not user.is_active:
                    msg = 'User account is disabled.'
                    raise exceptions.ValidationError(msg)
            else:
                msg = 'Unable to log in with provided credentials.'
                raise exceptions.ValidationError(msg)
        else:
            msg = 'Must include "email or username" and "password"'
            raise exceptions.ValidationError(msg)

        attrs['user'] = user
        return attrs
