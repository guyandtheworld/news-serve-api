import uuid
from django.db import models


STATUSES = (("active", "Active"), ("demo", "Demo"), ("retired", "Retired"))


class Entity(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    lei = models.CharField(max_length=100, blank=True)
    dbpediaResource = models.CharField(max_length=100, blank=True)
    wikiResource = models.CharField(max_length=100, blank=True)
    historyProcessed = models.BooleanField(default=False)
    entityType = models.CharField(max_length=100)
    manualEntry = models.BooleanField(default=False)
    def __str__(self):
        return self.name

class Alias(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    entityID = models.ForeignKey("Entity", on_delete=models.CASCADE)
    def __str__(self):
        return "{} - {}".format(self.name, self.entityID.name)


class LastScrape(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entityID = models.ForeignKey("Entity", on_delete=models.CASCADE)
    scrapeSourceID = models.ForeignKey("ScrapeSource", on_delete=models.CASCADE)
    lastScraped = models.DateTimeField()
    def __str__(self):
        return self.entityID


class ScrapeSource(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    scrapeInterval = models.IntegerField()
    def __str__(self):
        return self.name
