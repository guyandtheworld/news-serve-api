import uuid
from django.db import models
from django.contrib.postgres.fields import JSONField
from django.utils import timezone


STATUSES = (("active", "Active"), ("demo", "Demo"), ("retired", "Retired"))


class Story(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4,
                            editable=False)
    entityID = models.ForeignKey("Entity", on_delete=models.CASCADE)
    title = models.CharField(max_length=2000)
    unique_hash = models.CharField(max_length=100)
    url = models.CharField(max_length=1000)
    search_keyword = models.CharField(max_length=200)
    published_date = models.DateTimeField()
    internal_source = models.CharField(max_length=100)
    domain = models.CharField(max_length=150)
    language = models.CharField(max_length=100)
    source_country = models.CharField(max_length=100)
    raw_file_source = models.CharField(max_length=1000)
    entry_created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return "{} - {}".format(self.entityID.name, self.title)

    class Meta:
        verbose_name_plural = "stories"


class StoryBody(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4,
                            editable=False)
    storyID = models.ForeignKey("Story", on_delete=models.CASCADE)
    body = models.CharField(max_length=10000, blank=True, null=True)
    status_code = models.IntegerField(blank=True, null=True)
    entryTime = models.DateTimeField()

    def __str__(self):
        return "{}".format(self.storyID.title)

    class Meta:
        verbose_name_plural = "story bodies"


class StoryEntities(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4,
                            editable=False)
    storyID = models.ForeignKey("Story", on_delete=models.CASCADE)
    is_headline = models.BooleanField()
    entities = JSONField()
    entryTime = models.DateTimeField()

    def __str__(self):
        return "{}".format(self.storyID.title)

    class Meta:
        verbose_name_plural = "story entities"


class StorySentiment(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4,
                            editable=False)
    storyID = models.ForeignKey("Story", on_delete=models.CASCADE)
    is_headline = models.BooleanField()
    sentiment = JSONField()
    entryTime = models.DateTimeField()

    def __str__(self):
        return "{}".format(self.storyID.title)

    class Meta:
        verbose_name_plural = "story sentiment"


class BucketScore(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4,
                            editable=False)
    storyID = models.ForeignKey("Story", on_delete=models.CASCADE)
    entryTime = models.DateTimeField()
    sourceID = models.ForeignKey("Source", on_delete=models.CASCADE)
    bucketID = models.ForeignKey("Bucket", on_delete=models.CASCADE)
    modelID = models.ForeignKey("ModelDetail", on_delete=models.CASCADE)
    grossScore = models.FloatField()

    def __str__(self):
        return "{} - {}".format(self.storyID.name, self.bucketID.name)


class EntityScore(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4,
                            editable=False)
    storyID = models.ForeignKey("Story", on_delete=models.CASCADE)
    entryTime = models.DateTimeField()
    entityID = models.ForeignKey("Entity", on_delete=models.CASCADE)
    sourceID = models.ForeignKey("Source", on_delete=models.CASCADE)
    bucketID = models.ForeignKey("Bucket", on_delete=models.CASCADE)
    modelID = models.ForeignKey("ModelDetail", on_delete=models.CASCADE)
    grossScore = models.FloatField()

    def __str__(self):
        return "{} - {}".format(self.storyID.name, self.bucketID.name)
