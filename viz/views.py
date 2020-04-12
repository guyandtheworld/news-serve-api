import pandas as pd
from django.shortcuts import get_object_or_404

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework import views
from rest_framework.response import Response
from apis.models.users import DashUser
from apis.models.entity import Entity, StoryEntityRef
from apis.models.scenario import Bucket, Scenario

from .sql import (news_count_query,
                  bucket_score_query,
                  sentiment_query,
                  get_entity_stories)


class GenericGET(views.APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def getStories(self, entity_uuid, data, mode, metric_label):
        """
        For each given date, fetch and attach top 10
        relevant stories of the days depending on the
        entity.
        """
        df = pd.DataFrame(data, columns=["date", metric_label])
        dates = df['date'].apply(str).values

        # fetch and attach stories for particular dates
        stories = get_entity_stories(dates, entity_uuid, mode)
        stories = pd.DataFrame(stories, columns=["date", "stories"])

        df = df.merge(stories, how="left")
        df.fillna("", inplace=True)
        return df.to_dict('records')


class NewsCountViz(GenericGET):
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
            entity_uuid = request.data["entity_uuid"]
            if mode == "portfolio":
                entity = get_object_or_404(Entity,
                                           uuid=entity_uuid)
            else:
                entity = get_object_or_404(StoryEntityRef,
                                           uuid=entity_uuid)

            data = news_count_query("entity", entity.uuid, mode=mode)
            records = self.getStories(entity_uuid, data, mode, metric_label="count")
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

        return Response({"success": True, "length": len(records),
                         "data": records},
                        status=status.HTTP_200_OK)


class BucketScoreViz(GenericGET):
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
            entity_uuid = request.data["entity_uuid"]

            if mode == "portfolio":
                entity = get_object_or_404(Entity,
                                           uuid=entity_uuid)
            else:
                entity = get_object_or_404(StoryEntityRef,
                                           uuid=entity_uuid)

            data = bucket_score_query("entity",
                                      bucket.uuid,
                                      entity.uuid,
                                      scenario_id=bucket.scenarioID.uuid)

            records = self.getStories(entity_uuid, data, mode, metric_label="score")

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

        return Response({"success": True, "length": len(records),
                         "data": records},
                        status=status.HTTP_200_OK)


class SentimentViz(GenericGET):
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
            entity_uuid = request.data["entity_uuid"]

            if mode == "portfolio":
                entity = get_object_or_404(Entity,
                                           uuid=entity_uuid)
            else:
                entity = get_object_or_404(StoryEntityRef,
                                           uuid=entity_uuid)

            data = sentiment_query("entity",
                                   entity.uuid,
                                   request.data["sentiment_type"],
                                   scenario_id=scenario.uuid,
                                   mode=mode)

            records = self.getStories(
                entity_uuid, data, mode, metric_label="sentiment")
        # viz for bucket
        elif request.data["type"] == 'bucket':
            bucket = get_object_or_404(Bucket,
                                       uuid=request.data["bucket_uuid"])
            data = sentiment_query(
                "bucket", bucket.uuid, request.data["sentiment_type"], bucket.scenarioID.uuid)

            return Response({"success": True, "length": len(data),
                             "data": data},
                            status=status.HTTP_200_OK)

        else:
            msg = "no viz for this type"
            return Response({"success": False, "data": msg},
                            status=status.HTTP_404_NOT_FOUND)

        # if sentiment is negative, return negative time series
        if request.data["sentiment_type"] == "neg":
            for i in range(len(records)):
                records[i]["sentiment"] = -records[i]["sentiment"]

        return Response({"success": True, "length": len(records),
                         "data": records},
                        status=status.HTTP_200_OK)
