from rest_framework.serializers import ModelSerializer

from apis.models.entity import Entity
from apis.models.scenario import Scenario


class VerifiableEntitySerializer(ModelSerializer):
    class Meta:
        model = Entity
        fields = "__all__"


class EntityUpdateSerializer(ModelSerializer):
    class Meta:
        model = Entity
        exclude = ["uuid"]


class ScenarioListSerializer(ModelSerializer):
    class Meta:
        model = Scenario
        fields = ['name', 'mode', 'trackingDays', 'entityType', 'description']


class UnverifiedScenarioSerializer(ModelSerializer):
    class Meta:
        model = Scenario
        fields = "__all__"
