from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework import views
from rest_framework.response import Response
from apis.models.users import DashUser
from apis.models.entity import Entity, StoryEntityRef
from apis.models.scenario import Bucket, Scenario

from .sql import news_count_query, bucket_score_query, sentiment_query


class NewsCountViz(views.APIView):
    """
    For a given entity or a bucket, get
    * News Count Per Day
    """

    def post(self, request, format=None):
        get_object_or_404(DashUser, uuid=request.data["user"])

        if "mode" in request.data:
            mode = request.data["mode"]
        else:
            mode = "portfolio"

        # viz for entities
        if request.data["type"] == 'entity':
            if mode == "portfolio":
                entity = get_object_or_404(Entity,
                                           uuid=request.data["entity_uuid"])
            else:
                entity = get_object_or_404(StoryEntityRef,
                                           uuid=request.data["entity_uuid"])

            data = news_count_query("entity", entity.uuid, mode=mode)
            return Response({"success": True, "length": len(data),
                             "data": data},
                            status=status.HTTP_200_OK)
        # viz for bucket
        elif request.data["type"] == 'bucket':
            bucket = get_object_or_404(Bucket,
                                       uuid=request.data["bucket_uuid"])
            data = news_count_query("bucket", bucket.uuid,
                                    bucket.scenarioID.uuid)
            return Response({"success": True, "length": len(data),
                             "data": data},
                            status=status.HTTP_200_OK)
        else:
            msg = "no viz for this type"
            return Response({"success": False, "data": msg},
                            status=status.HTTP_404_NOT_FOUND)


class BucketScoreViz(views.APIView):
    """
    For a given entity or a bucket, get
    * Normalized Bucket Score Per Day (all buckets)
    """

    def post(self, request, format=None):
        get_object_or_404(DashUser, uuid=request.data["user"])
        bucket = get_object_or_404(Bucket, uuid=request.data['bucket_uuid'])

        if "mode" in request.data:
            mode = request.data["mode"]
        else:
            mode = "portfolio"

        # viz for entity and bucket
        if request.data["type"] == 'entity':
            if mode == "portfolio":
                entity = get_object_or_404(Entity,
                                           uuid=request.data["entity_uuid"])
            else:
                entity = get_object_or_404(StoryEntityRef,
                                           uuid=request.data["entity_uuid"])

            data = bucket_score_query("entity",
                                      bucket.uuid,
                                      entity.uuid,
                                      scenario_id=bucket.scenarioID.uuid)

            return Response({"success": True, "length": len(data),
                             "data": data},
                            status=status.HTTP_200_OK)
        # viz for just buckets
        if request.data["type"] == 'bucket':
            data = bucket_score_query("bucket",
                                      bucket.uuid,
                                      scenario_id=bucket.scenarioID.uuid)
            return Response({"success": True, "length": len(data),
                             "data": data},
                            status=status.HTTP_200_OK)
        else:
            msg = "no viz for this type"
            return Response({"success": False, "data": msg},
                            status=status.HTTP_404_NOT_FOUND)


class SentimentViz(views.APIView):
    """
    For a given entity or a bucket, get
    * Normalized sentiment per day (compound/-ve/+ve)
    """

    def post(self, request, format=None):

        get_object_or_404(DashUser, uuid=request.data["user"])
        scenario = get_object_or_404(Scenario, uuid=request.data["scenario_uuid"])

        if "mode" in request.data:
            mode = request.data["mode"]
        else:
            mode = "portfolio"

        # viz for entities
        if request.data["type"] == 'entity':
            if mode == "portfolio":
                entity = get_object_or_404(Entity,
                                           uuid=request.data["entity_uuid"])
            else:
                entity = get_object_or_404(StoryEntityRef,
                                           uuid=request.data["entity_uuid"])

            data = sentiment_query("entity",
                                   entity.uuid,
                                   request.data["sentiment_type"],
                                   scenario_id=scenario.uuid,
                                   mode=mode)
        # viz for bucket
        elif request.data["type"] == 'bucket':
            bucket = get_object_or_404(Bucket,
                                       uuid=request.data["bucket_uuid"])
            data = sentiment_query(
                "bucket", bucket.uuid, request.data["sentiment_type"], bucket.scenarioID.uuid)
        else:
            msg = "no viz for this type"
            return Response({"success": False, "data": msg},
                            status=status.HTTP_404_NOT_FOUND)

        # if sentiment is negative, return negative time series
        if request.data["sentiment_type"] == "neg":
            print("reversing")
            for i in range(len(data)):
                data[i][list(data[i].keys())[0]] = -data[i][list(data[i].keys())[0]]

        return Response({"success": True, "length": len(data),
                         "data": data},
                        status=status.HTTP_200_OK)
