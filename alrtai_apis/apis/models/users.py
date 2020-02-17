import uuid
from django.db import models

STATUSES = (("active", "Active"), ("demo", "Demo"), ("retired", "Retired"))


class Client(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)


class User(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    password = models.CharField(max_length=256)
    status = models.CharField(max_length=10, choices=STATUSES)
    clientID = models.ForeignKey("Client", on_delete=models.CASCADE)
    defaultScenario = models.ForeignKey("Scenario", on_delete=models.CASCADE)
    setupDate = models.DateField()


class UserScenario(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    userID = models.ForeignKey("User", on_delete=models.CASCADE)
    scenarioID = models.ForeignKey("Scenario", on_delete=models.CASCADE)


class Portfolio(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    userID = models.ForeignKey("User", on_delete=models.CASCADE)
    scenarioID = models.ForeignKey("Scenario", on_delete=models.CASCADE)
    entityID = models.ForeignKey("Entity", on_delete=models.CASCADE)
