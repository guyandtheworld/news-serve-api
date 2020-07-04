import uuid
from django.db import models
from django.contrib.postgres.fields import ArrayField


STATUSES = (("active", "Active"), ("demo", "Demo"), ("retired", "Retired"))
ENTRY = (("custom", "Custom"), ("auto", "Auto"))


class Entity(models.Model):
    uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    scenarioID = models.ForeignKey("Scenario", on_delete=models.CASCADE,
                                   related_name='entity')
    lei = models.CharField(max_length=100, blank=True)
    dbpediaResource = models.CharField(max_length=100, blank=True)
    wikipedia = models.CharField(max_length=200, blank=True)
    historyProcessed = models.BooleanField(default=False)
    typeID = models.ForeignKey("EntityType", on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    entryVerified = models.BooleanField(default=False)
    manualEntry = models.BooleanField(default=False)
    keywords = ArrayField(models.CharField(max_length=200), null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "entities"


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


class StoryEntityRef(models.Model):
    uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    typeID = models.ForeignKey("EntityType", on_delete=models.CASCADE)
    wikipedia = models.CharField(max_length=200, blank=True)
    render = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey("DashUser", null=True, on_delete=models.SET_NULL)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return "{} - {}".format(self.name, self.typeID.name)


class StoryEntityMap(models.Model):
    uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    entityID = models.ForeignKey("StoryEntityRef", on_delete=models.CASCADE)
    storyID = models.ForeignKey("Story", on_delete=models.CASCADE)
    # change null=True later
    salience = models.FloatField(null=True)
    mentions = models.IntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey("DashUser", null=True, on_delete=models.SET_NULL)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    last_value = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return "{} - {}".format(self.storyID.title, self.entityID.name)


class EntityType(models.Model):
    uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    entry = models.CharField(max_length=10, choices=ENTRY)

    def __str__(self):
        return self.name
