import uuid
from django.db import models


class Alias(models.Model):
    uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    wikipedia = models.CharField(max_length=200, blank=True)
    score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    typeID = models.ForeignKey("apis.EntityType", on_delete=models.CASCADE)
    parentID = models.ForeignKey("apis.StoryEntityRef", on_delete=models.CASCADE)
    updated_by = models.ForeignKey(
        "apis.DashUser", null=True, on_delete=models.SET_NULL)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    last_value = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return "{} - {}".format(self.name, self.typeID.name)

    class Meta:
        verbose_name_plural = "Alias"


class Dump(models.Model):
    """
    Store all the Entities extracted from Stories
    """
    uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    typeID = models.ForeignKey("apis.EntityType", on_delete=models.CASCADE)
    wikipedia = models.CharField(max_length=200, blank=True)
    render = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    storyID = models.ForeignKey("apis.Story", on_delete=models.CASCADE)
    published_date = models.DateTimeField()
    salience = models.FloatField(null=True)
    mentions = models.IntegerField(null=True)
    updated_by = models.ForeignKey("apis.DashUser", null=True, on_delete=models.SET_NULL)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return "{} - {}".format(self.name, self.typeID.name)


class Custom(models.Model):
    """
    Custom Entities defined in a Scenario to detect terms.
    Dump into EntityDump using the same CustomEntity UUID.
    """
    uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    typeID = models.ForeignKey("apis.EntityType", on_delete=models.CASCADE)
    scenarioID = models.ForeignKey("apis.Scenario", on_delete=models.CASCADE)
    wikipedia = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    salience = models.FloatField(null=True)
    mentions = models.IntegerField(null=True)
    updated_by = models.ForeignKey("apis.DashUser", null=True, on_delete=models.SET_NULL)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return "{} - {}".format(self.name, self.typeID.name)
