from rest_framework.serializers import ModelSerializer

from apis.models.entity import Entity, Alias


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
