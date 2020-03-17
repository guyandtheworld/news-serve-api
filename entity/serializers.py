from rest_framework.serializers import ModelSerializer

from apis.models.entity import Entity, Alias


class AliasSerializer(ModelSerializer):
    class Meta:
        model = Alias
        fields = ("uuid", "name",)


class EntitySerializer(ModelSerializer):
    alias = AliasSerializer(many=True)

    class Meta:
        model = Entity
        fields = [field.name for field in model._meta.fields]
        fields.append('alias')
