from django.shortcuts import get_object_or_404

from rest_framework import views
from rest_framework.response import Response
from apis.models.users import DashUser
from apis.models.entity import Entity
from apis.models.scenario import Bucket
from apis.models.scenario import Scenario

from .sql import news_count_query,bucket_score_query,sentiment_query


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

class BucketScoreViz(views.APIView):
    """
    For a given entity or a bucket, get
    * Normalized Bucket Score Per Day (all buckets)
    """
    def post(self, request, format=None):
        user = get_object_or_404(DashUser, uuid=request.data["user"])
        bucket= get_object_or_404(Bucket, uuid=request.data['bucket_uuid'])
        scenario = get_object_or_404(Scenario,
                                            uuid=request.data['scenario_uuid'])
        # viz for entities
        if request.data["type"] == 'entity':
            entity = get_object_or_404(Entity,
                                       uuid=request.data["entity_uuid"])
            data = bucket_score_query("entity",
                                        bucket.uuid, entity.uuid,scenario.uuid)
            return Response({"success": True, "length": len(data),
                             "data": data})
        # viz for bucket
        if request.data["type"] == 'bucket':
            data = bucket_score_query("bucket",
                                        bucket.uuid, scenario_id=scenario.uuid)
            return Response({"success": True, "length": len(data),
                             "data": data})
        else:
            msg = "no viz for this type"
            return Response({"success": False, "data": msg})

class SentimentViz(views.APIView):
    """
    For a given entity or a bucket, get 
    * Normalized sentiment per day (compound/-ve/+ve)
    """
    def post(self, request, format=None):
        
        user = get_object_or_404(DashUser, uuid=request.data["user"])

        # viz for entities
        if request.data["type"] == 'entity':
            entity = get_object_or_404(Entity,
                                       uuid=request.data["entity_uuid"])
            data = sentiment_query("entity", entity.uuid, request.data["sentiment_type"], entity.scenarioID.uuid)
            return Response({"success": True, "length": len(data),
                             "data": data})
        # viz for bucket
        elif request.data["type"] == 'bucket':
            bucket = get_object_or_404(Bucket,
                                       uuid=request.data["bucket_uuid"])
            data = sentiment_query("bucket", bucket.uuid, request.data["sentiment_type"], bucket.scenarioID.uuid)
            return Response({"success": True, "length": len(data),
                             "data": data})
        else:
            msg = "no viz for this type"
            return Response({"success": False, "data": msg})
