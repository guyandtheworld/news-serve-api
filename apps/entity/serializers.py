from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from apis.models.entity import Entity, StoryEntityRef
from apis.models.users import Portfolio


class EntityListSerializer(ModelSerializer):
    class Meta:
        model = Entity
        fields = "__all__"


class PortfolioListSerializer(ModelSerializer):
    entities = EntityListSerializer(many=True)

    class Meta:
        model = Portfolio
        fields = [field.name for field in model._meta.fields]
        fields.append('entities')


class EntitySerializer(ModelSerializer):
    class Meta:
        model = Entity
        exclude = ["uuid"]


class PortfolioSerializer(ModelSerializer):
    class Meta:
        model = Portfolio
        exclude = ["uuid"]


class StoryEntityRefSerializer(ModelSerializer):
    entity_type = serializers.CharField(source='typeID.name', read_only=True)

    class Meta:
        model = StoryEntityRef
        fields = [field.name for field in model._meta.fields]
        fields.append('entity_type')
