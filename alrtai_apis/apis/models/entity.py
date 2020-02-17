import uuid
from django.db import models


STATUSES = (("active", "Active"), ("demo", "Demo"), ("retired", "Retired"))


class Entity(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    lei = models.CharField(max_length=100)
    dbpediaResource = models.CharField(max_length=100)
    wikiResource = models.CharField(max_length=100)
    historyProcessed = models.BooleanField(default=False)
    entityType = models.CharField(max_length=100)
    manualEntry = models.BooleanField(default=False)


class Alias(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    entityID = models.ForeignKey("Entity", on_delete=models.CASCADE)


class LastScraped(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entityID = models.ForeignKey("Entity", on_delete=models.CASCADE)
    scrapeSourceID = models.ForeignKey("ScrapeSource", on_delete=models.CASCADE)
    lastScraped = models.DateTimeField()


class ScrapeSource(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    scrapeInterval = models.IntegerField()
