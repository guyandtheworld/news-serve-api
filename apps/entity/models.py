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

    def __str__(self):
        return "{} - {}".format(self.name, self.typeID.name)

    class Meta:
        verbose_name_plural = "Alias"
