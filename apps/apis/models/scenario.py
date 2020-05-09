import uuid
from django.db import models
from django.contrib.postgres.fields import ArrayField
from .users import STATUSES


MODES = (("portfolio", "Portfolio"), ("auto", "Auto"))


class Scenario(models.Model):
    uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    status = models.CharField(max_length=10, choices=STATUSES)
    mode = models.CharField(max_length=10, choices=MODES)
    trackingDays = models.SmallIntegerField()
    entityType = models.ForeignKey("EntityType", on_delete=models.PROTECT)
    description = models.CharField(max_length=250, blank=True)

    def __str__(self):
        return self.name


class Bucket(models.Model):
    uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    model_label = models.CharField(max_length=100)
    scenarioID = models.ForeignKey("Scenario", on_delete=models.CASCADE,
                                   related_name='bucket')
    description = models.CharField(max_length=250, blank=True)
    keywords = ArrayField(models.CharField(max_length=200), null=True, blank=True)

    def __str__(self):
        return self.name


class BucketWeight(models.Model):
    uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    bucketID = models.ForeignKey("Bucket", on_delete=models.CASCADE)
    userID = models.ForeignKey("DashUser", on_delete=models.CASCADE)
    weight = models.FloatField()

    def __str__(self):
        return self.bucketID + self.userID


class ModelDetail(models.Model):
    uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    scenarioID = models.ForeignKey("Scenario", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    version = models.SmallIntegerField()
    bucket = models.CharField(max_length=100)
    storage_link = models.CharField(max_length=100)

    def __str__(self):
        return "{} - {}".format(self.name, self.version)


class BucketModel(models.Model):
    uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    bucketID = models.ForeignKey("Bucket", on_delete=models.CASCADE)
    modelID = models.ForeignKey("ModelDetail", on_delete=models.CASCADE)

    def __str__(self):
        return "{} - {} - V{}".format(self.bucketID.name, self.modelID.name,
                                      self.modelID.version)


class Source(models.Model):
    uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    score = models.FloatField()

    def __str__(self):
        return self.name


class Keywords(models.Model):
    uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    scenarioID = models.ForeignKey("Scenario", on_delete=models.CASCADE)
    keywords = ArrayField(models.CharField(max_length=100), blank=True, default=list)

    def __str__(self):
        return "{}".format(self.scenarioID)
