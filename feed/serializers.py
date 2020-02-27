from rest_framework import serializers
from apis.models.story import Story


class StorySerializer(serializers.ModelSerializer):

    # story_body = serializers.RelatedField(many=True)

    class Meta:
        model = Story
        fields = '__all__'


class StoryBodySerializer(serializers.ModelSerializer):
    pass
    # StoryBody
    # StoryEntities
    # StorySentiment
