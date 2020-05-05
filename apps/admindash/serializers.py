from rest_framework.serializers import ModelSerializer

from apis.models.entity import Entity, Alias
from apis.models.scenario import Scenario


class AliasListSerializer(ModelSerializer):
    class Meta:
        model = Alias
        fields = ("uuid", "name",)


class VerifiableEntitySerializer(ModelSerializer):
    alias = AliasListSerializer(many=True)

    class Meta:
        model = Entity
        fields = [field.name for field in model._meta.fields]
        fields.append('alias')


class EntityUpdateSerializer(ModelSerializer):
    class Meta:
        model = Entity
        exclude = ["uuid"]


class AliasUpdateSerializer(ModelSerializer):
    class Meta:
        model = Entity
        fields = ['name']


class ScenarioListSerializer(ModelSerializer):
    class Meta:
        model = Scenario
        fields = ['name', 'mode', 'trackingDays', 'entityType', 'description']


class UnverifiedScenarioSerializer(ModelSerializer):
    class Meta:
        model = Scenario
        fields = "__all__"
