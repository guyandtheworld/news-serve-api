import uuid

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


STATUSES = (("active", "Active"), ("demo", "Demo"), ("retired", "Retired"), ("unverified", "Unverified"))

ROLES = (("alrt-admin", "Alrt Admin"), ("alrt-sme", "Alrt SME"), ("alrt-qa", "Alrt QA"),
         ("demo-user", "Demo User"), ("client-admin", "Client Admin"), ("client-user", "Client User"))

ACCESS = (("view", "View"), ("edit", "Edit"))


class Client(models.Model):
    uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class DashUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4,
                            editable=False)
    status = models.CharField(max_length=10, choices=STATUSES)
    role = models.CharField(max_length=25, choices=ROLES)
    clientID = models.ForeignKey("Client", on_delete=models.CASCADE)
    defaultScenario = models.ForeignKey("Scenario", on_delete=models.CASCADE)
    setupDate = models.DateField(default=timezone.now)

    def __str__(self):
        return "{} {}".format(self.user.first_name, self.user.last_name)


class UserScenario(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4,
                            editable=False)
    access = models.CharField(max_length=10, choices=ACCESS)
    userID = models.ForeignKey("DashUser", on_delete=models.CASCADE)
    scenarioID = models.ForeignKey("Scenario", on_delete=models.CASCADE)

    def __str__(self):
        return "{} - {}".format(self.userID.user.username,
                                self.scenarioID.name)


class Portfolio(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4,
                            editable=False)
    userID = models.ForeignKey("DashUser", on_delete=models.CASCADE)
    scenarioID = models.ForeignKey("Scenario", on_delete=models.CASCADE)
    entityID = models.ForeignKey("Entity", on_delete=models.CASCADE,
                                 related_name="entities")

    def __str__(self):
        return "{} - {} - {}".format(self.userID.user.username,
                                     self.scenarioID.name,
                                     self.entityID.name)

    class Meta:
        verbose_name_plural = "portfolios"
