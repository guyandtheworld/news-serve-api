import uuid
from django.db import models


STATUSES = (("active", "Active"), ("demo", "Demo"), ("retired", "Retired"))


class Story(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entityID = models.ForeignKey("Entity", on_delete=models.CASCADE)
    title = models.CharField(max_length=1000)
    unique_hash = models.CharField(max_length=100)
    url = models.CharField(max_length=100)
    search_keyword = models.CharField(max_length=100)
    published_date = models.DateTimeField()
    description = models.CharField(max_length=1000)
    body = models.CharField(max_length=10000)
    status_code = models.IntegerField()
    internal_source = models.CharField(max_length=100)
    domain = models.CharField(max_length=100)
    entry_created = models.DateTimeField()
    language = models.CharField(max_length=100)
    source_country = models.CharField(max_length=100)
    raw_file_source = models.CharField(max_length=100)
    # title_analytics
    # body_analytics


class BucketScore(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # storyID = models.ForeignKey("Story", on_delete=models.CASCADE)
    storyID = models.CharField(max_length=100)
    storyDate = models.DateTimeField()
    sourceID = models.ForeignKey("Source", on_delete=models.CASCADE)
    bucketID = models.ForeignKey("Bucket", on_delete=models.CASCADE)
    modelID = models.ForeignKey("ModelDetail", on_delete=models.CASCADE)
    grossScore = models.FloatField()


class EntityScore(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # storyID = models.ForeignKey("Story", on_delete=models.CASCADE)
    storyID = models.CharField(max_length=1000)
    entityID = models.ForeignKey("Entity", on_delete=models.CASCADE)
    sourceID = models.ForeignKey("Source", on_delete=models.CASCADE)
    bucketID = models.ForeignKey("Bucket", on_delete=models.CASCADE)
    modelID = models.ForeignKey("ModelDetail", on_delete=models.CASCADE)
    grossScore = models.FloatField()
