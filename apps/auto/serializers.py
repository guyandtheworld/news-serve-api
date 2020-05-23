from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from apis.models.story import EntityScore
from apis.models.entity import (EntityType, 
                                StoryEntityRef, 
                                StoryEntityMap)
from entity.models import Alias


class EntityTypeSerializer(ModelSerializer):
    class Meta:
        model = EntityType
        fields = "__all__"


class AliasListSerializer(ModelSerializer):
    entity_type = serializers.CharField(source='typeID.name', read_only=True)
    class Meta:
        model = Alias
        fields = [field.name for field in model._meta.fields]
        fields.append('entity_type')


class ParentNameSerializer(ModelSerializer):
    class Meta:
        model = StoryEntityRef
        fields = ["name"]


class StoryEntityMapSerializer(ModelSerializer):
    class Meta:
        model = StoryEntityMap
        fields = ["entityID"]


class EntityScoreSerializer(ModelSerializer):
    class Meta:
        model = EntityScore
        fields = ["entityID"]


class AliasChangeSerializer(ModelSerializer):
    class Meta:
        model = Alias
        fields = ["parentID"]
