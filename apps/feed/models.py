import uuid
from django.db import models


from django.contrib.postgres.fields import JSONField


class Cluster(models.Model):
    """
    Table for storing each new entities and their
    respective scores on the go.
    """
    uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    cluster = models.IntegerField()
    name = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        db_table = 'ml_cluster'

    def __str__(self):
        return "{}".format(self.cluster)


class ClusterMap(models.Model):
    """
    Table for storing each new entities and their
    respective scores on the go.
    """
    uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    storyID = models.ForeignKey("apis.Story", on_delete=models.CASCADE)
    clusterID = models.ForeignKey("Cluster", on_delete=models.CASCADE)
    published_date = models.DateTimeField()

    class Meta:
        db_table = 'ml_clustermap'

    def __str__(self):
        return "{}".format(self.storyID.title)


class PortfolioWarehouse(models.Model):
    """
    Table for storing each stories and their
    respective scores on the go.
    """

    uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    storyID = models.UUIDField()
    title = models.CharField(max_length=2000)
    url = models.CharField(max_length=1000)
    published_date = models.DateTimeField()  # timezone localized date
    domain = models.CharField(max_length=150)
    language = models.CharField(max_length=100)
    source_country = models.CharField(max_length=100)
    search_keyword = models.CharField(max_length=200)
    entity_name = models.CharField(max_length=200)
    entityID = models.UUIDField()
    scenarioID = models.UUIDField()
    story_body = models.CharField(max_length=10000)
    timestamp = models.DateTimeField()
    cluster = models.IntegerField()
    scores = JSONField()  # gross score, source score
    entities = JSONField()
    hotness = JSONField()
    bucket_scores = JSONField()
    sentiment = JSONField()

    def __str__(self):
        return "{}".format(self.story_title)


class AutoWarehouse(models.Model):
    """
    Table for storing each stories and their
    respective scores on the go.
    """

    uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    storyID = models.UUIDField()
    title = models.CharField(max_length=2000)
    url = models.CharField(max_length=1000)
    published_date = models.DateTimeField()
    domain = models.CharField(max_length=150)
    language = models.CharField(max_length=100)
    source_country = models.CharField(max_length=100)
    search_keyword = models.CharField(max_length=200)
    entity_name = models.CharField(max_length=200)
    entityID = models.UUIDField()
    scenarioID = models.UUIDField()
    story_body = models.CharField(max_length=10000)
    timestamp = models.DateTimeField()
    cluster = models.IntegerField()
    scores = JSONField()  # gross score, source score
    entities = JSONField()
    hotness = JSONField()
    bucket_scores = JSONField()
    sentiment = JSONField()

    def __str__(self):
        return "{}".format(self.story_title)
