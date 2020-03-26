from rest_framework import serializers
from apis.models.story import Story, StoryBody, StorySentiment


class StoryBodySerializer(serializers.ModelSerializer):
    story = serializers.RelatedField(read_only=True)

    class Meta:
        model = StoryBody
        fields = ('body', 'story')


class StorySentimentSerializer(serializers.ModelSerializer):
    story = serializers.RelatedField(read_only=True)

    class Meta:
        model = StorySentiment
        fields = ('is_headline', 'sentiment', 'story')


class StorySerializer(serializers.ModelSerializer):

    story_body = StoryBodySerializer(read_only=True, many=True)
    story_sentiment = StorySentimentSerializer(read_only=True, many=True)

    class Meta:
        model = Story
        fields = [field.name for field in model._meta.fields]
        fields.append('story_body')
        fields.append('story_sentiment')
