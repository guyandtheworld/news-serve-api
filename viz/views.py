from django.shortcuts import get_object_or_404

from rest_framework import views
from rest_framework.response import Response
from apis.models.users import DashUser
from apis.models.entity import Entity
from apis.models.scenario import Bucket

from .sql import news_count_query


class NewsCountViz(views.APIView):
    """
    For a given entity or a bucket, get
    * News Count Per Day
    """
    def post(self, request, format=None):
        user = get_object_or_404(DashUser, uuid=request.data["user"])

        # viz for entities
        if request.data["type"] == 'entity':
            entity = get_object_or_404(Entity,
                                       uuid=request.data["entity_uuid"])
            data = news_count_query("entity", entity.uuid)
            return Response({"success": True, "length": len(data),
                             "data": data})
        # viz for bucket
        elif request.data["type"] == 'bucket':
            bucket = get_object_or_404(Bucket,
                                       uuid=request.data["bucket_uuid"])
            data = news_count_query("bucket", bucket.uuid,
                                    bucket.scenarioID.uuid)
            return Response({"success": True, "length": len(data),
                             "data": data})
        else:
            msg = "no viz for this type"
            return Response({"success": False, "data": msg})
