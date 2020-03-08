from rest_framework.serializers import ModelSerializer
from .models.entity import Entity, Alias


class EntitySerializer(ModelSerializer):

    class Meta:
        model = Entity
        exclude = ["uuid"]


class AliasSerializer(ModelSerializer):
    class Meta:
        model = Alias
        exclude = ["uuid"]
