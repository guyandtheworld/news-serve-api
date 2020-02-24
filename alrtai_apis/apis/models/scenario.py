import uuid
from django.db import models
from .users import STATUSES


class Scenario(models.Model):
    uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    status = models.CharField(max_length=10, choices=STATUSES)
    trackingDays = models.SmallIntegerField()

    def __str__(self):
        return self.name


class Bucket(models.Model):
    uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    scenarioID = models.ForeignKey("Scenario", on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class BucketWeight(models.Model):
    uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    bucketID = models.ForeignKey("Bucket", on_delete=models.CASCADE)
    userID = models.ForeignKey("User", on_delete=models.CASCADE)
    weight = models.FloatField()

    def __str__(self):
        return self.bucketID + self.userID


class ModelDetail(models.Model):
    uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    version = models.SmallIntegerField()
    storage_link = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class BucketModel(models.Model):
    uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    bucketID = models.ForeignKey("Bucket", on_delete=models.CASCADE)
    modelID = models.ForeignKey("ModelDetail", on_delete=models.CASCADE)

    def __str__(self):
        return self.bucketID + self.modelID


class Source(models.Model):
    uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    url = models.URLField()
    score = models.FloatField()

    def __str__(self):
        return self.name
