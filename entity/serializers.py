from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from apis.models.entity import Entity, Alias, StoryEntityRef, EntityType
from apis.models.users import Portfolio


class AliasListSerializer(ModelSerializer):
    class Meta:
        model = Alias
        fields = ("uuid", "name",)


class EntityListSerializer(ModelSerializer):
    alias = AliasListSerializer(many=True)

    class Meta:
        model = Entity
        fields = [field.name for field in model._meta.fields]
        fields.append('alias')


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


class AliasSerializer(ModelSerializer):
    class Meta:
        model = Alias
        exclude = ["uuid"]


class PortfolioSerializer(ModelSerializer):
    class Meta:
        model = Portfolio
        exclude = ["uuid"]


class StoryEntityRefSerializer(ModelSerializer):
    type_id = serializers.UUIDField(source='typeID.uuid', read_only=True)
    entity_type = serializers.CharField(source='typeID.name', read_only=True)

    class Meta:
        model = StoryEntityRef
        fields = [field.name for field in model._meta.fields]
        fields.append('entity_type')
        fields.append('type_id')
