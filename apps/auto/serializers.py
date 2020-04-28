from rest_framework.serializers import ModelSerializer

from apis.models.entity import EntityType


class EntityTypeSerializer(ModelSerializer):
    class Meta:
        model = EntityType
        fields = "__all__"
