from rest_framework.serializers import ModelSerializer

from apis.models.entity import Entity
from apis.models.scenario import Scenario, Bucket


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
