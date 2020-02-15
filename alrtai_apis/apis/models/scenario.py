import uuid
from django.db import models
from .users import STATUSES


class Scenario(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    status = models.CharField(max_length=10, choices=STATUSES)
    trackingDays = models.SmallIntegerField()


class Bucket(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    scenarioID = models.ForeignKey("Scenario", on_delete=models.CASCADE)


class BucketWeight(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bucketID = models.ForeignKey("Bucket", on_delete=models.CASCADE)
    userID = models.ForeignKey("User", on_delete=models.CASCADE)
    weight = models.FloatField()

