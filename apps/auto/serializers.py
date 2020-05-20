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
    class Meta:
        model = Alias
        fields = "__all__"


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
