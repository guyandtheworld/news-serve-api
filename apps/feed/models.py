import uuid
from django.db import models


class Cluster(models.Model):
    """
    Table for storing each new entities and their
    respective scores on the go.
    """
    uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    cluster = models.IntegerField()
    name = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        db_table = 'ml_cluster'

    def __str__(self):
        return "{}".format(self.cluster)


class ClusterMap(models.Model):
    """
    Table for storing each new entities and their
    respective scores on the go.
    """
    uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    storyID = models.ForeignKey("apis.Story", on_delete=models.CASCADE)
    clusterID = models.ForeignKey("Cluster", on_delete=models.CASCADE)

    class Meta:
        db_table = 'ml_clustermap'

    def __str__(self):
        return "{}".format(self.storyID.title)
