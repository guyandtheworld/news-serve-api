import uuid
from django.db import models


STATUSES = (("active", "Active"), ("demo", "Demo"), ("retired", "Retired"))


class Entity(models.Model):
    uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    scenarioID = models.ForeignKey("Scenario", on_delete=models.CASCADE)
    lei = models.CharField(max_length=100, blank=True)
    dbpediaResource = models.CharField(max_length=100, blank=True)
    wikiResource = models.CharField(max_length=100, blank=True)
    historyProcessed = models.BooleanField(default=False)
    entityType = models.CharField(max_length=100)
    entryVerified = models.BooleanField(default=False)
    manualEntry = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "entities"


class Alias(models.Model):
    uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    entityID = models.ForeignKey("Entity", on_delete=models.CASCADE)

    def __str__(self):
        return "{} - {}".format(self.name, self.entityID.name)

    class Meta:
        verbose_name_plural = "alias"


class LastScrape(models.Model):
    uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    entityID = models.ForeignKey("Entity", on_delete=models.CASCADE)
    scrapeSourceID = models.ForeignKey(
        "ScrapeSource", on_delete=models.CASCADE)
    lastScraped = models.DateTimeField()

    def __str__(self):
        return "{} - {} - {}".format(self.entityID.name,
                                     self.scrapeSourceID.name, str(self.lastScraped))

    class Meta:
        verbose_name_plural = "last scrapes"


class ScrapeSource(models.Model):
    uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    scrapeInterval = models.IntegerField()

    def __str__(self):
        return self.name
