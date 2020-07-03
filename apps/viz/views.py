import numpy as np
import pandas as pd

from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework import views
from rest_framework.response import Response
from apis.models.users import DashUser

from apis.models.entity import Entity, StoryEntityRef
from apis.models.scenario import Bucket, Scenario
from apis.utils import extract_timeperiod


from .sql import (news_count_query,
                  bucket_score_query,
                  sentiment_query,
                  get_entity_stories,
                  get_count_per_country)

from hdx.location.country import Country


class GenericGET(views.APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def getStories(self, entity_uuid, data, mode, metric_label):
        """
        For each given date, fetch and attach top 10
        relevant stories of the days depending on the
        entity.
        """
        if len(data) == 0:
            return []
        df = pd.DataFrame(data, columns=["date", metric_label])
        dates = df['date'].apply(str).values

        # fetch and attach stories for particular dates
        stories = get_entity_stories(dates, entity_uuid, mode)
        stories = pd.DataFrame(stories, columns=["date", "stories"])

        df = df.merge(stories, how="left")
        df.fillna("", inplace=True)
        return df.to_dict('records')

    def rolling_mean(self, agg, prop='W'):
        """given data returns the rolling weekly mean of news count"""

        date = []
        count = []
        for i in agg:
            date.append(list(i.keys())[0])
            count.append(list(i.values())[0])

        df = pd.DataFrame({'date': date, 'value': count})
        df['date'] = pd.to_datetime(df['date'].values)
        df = df.groupby('date')['value'].agg(sum)

        df = df.resample(prop).agg(np.mean).fillna(0)

        data = []
        for i, v in zip(df.index.values, df.values):
            data.append({str(i)[:10]: v})

        return data


class NewsCountViz(GenericGET):
    """
    For a given entity or a bucket, get
    * News Count Per Day
    """

    def post(self, request, format=None):
        get_object_or_404(DashUser, uuid=request.data["user"])
        dates = extract_timeperiod(request)
        # viz for entities
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

            data = news_count_query("entity", entity.uuid, dates, mode=mode)
        # viz for bucket
        elif request.data["type"] == 'bucket':
            bucket = get_object_or_404(Bucket,
                                       uuid=request.data["bucket_uuid"])
            data = news_count_query("bucket", bucket.uuid, dates,
                                    bucket.scenarioID.uuid)
        else:
            msg = "no viz for this type"
            return Response({"success": False, "data": msg},
                            status=status.HTTP_404_NOT_FOUND)

        if "rolling" in request.data.keys() and request.data["rolling"]:
            data = self.rolling_mean(data)

        return Response({"success": True, "length": len(data),
                         "data": data},
                        status=status.HTTP_200_OK)


class BucketScoreViz(GenericGET):
    """
    For a given entity or a bucket, get
    * Normalized Bucket Score Per Day (all buckets)
    """

    def post(self, request, format=None):
        get_object_or_404(DashUser, uuid=request.data["user"])
        bucket = get_object_or_404(Bucket, uuid=request.data['bucket_uuid'])
        dates = extract_timeperiod(request)
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
                                      dates,
                                      entity.uuid,
                                      scenario_id=bucket.scenarioID.uuid)
        # viz for just buckets
        elif request.data["type"] == 'bucket':
            data = bucket_score_query("bucket",
                                      bucket.uuid,
                                      dates,
                                      scenario_id=bucket.scenarioID.uuid)
        else:
            msg = "no viz for this type"
            return Response({"success": False, "data": msg},
                            status=status.HTTP_404_NOT_FOUND)

        if "rolling" in request.data.keys() and request.data["rolling"]:
            data = self.rolling_mean(data)

        return Response({"success": True, "length": len(data),
                         "data": data},
                        status=status.HTTP_200_OK)


class SentimentViz(GenericGET):
    """
    For a given entity or a bucket, get
    * Normalized sentiment per day (compound/-ve/+ve)
    """

    def post(self, request, format=None):

        get_object_or_404(DashUser, uuid=request.data["user"])
        scenario = get_object_or_404(Scenario, uuid=request.data["scenario_uuid"])
        dates = extract_timeperiod(request)
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
                                   dates,
                                   scenario_id=scenario.uuid,
                                   mode=mode)

        # viz for bucket
        elif request.data["type"] == 'bucket':
            bucket = get_object_or_404(Bucket,
                                       uuid=request.data["bucket_uuid"])
            data = sentiment_query(
                "bucket",
                bucket.uuid,
                request.data["sentiment_type"],
                dates,
                bucket.scenarioID.uuid)

        else:
            msg = "no viz for this type"
            return Response({"success": False, "data": msg},
                            status=status.HTTP_404_NOT_FOUND)

        # if sentiment is negative, return negative time series
        if request.data["sentiment_type"] == "neg":
            for i in range(len(data)):
                data[i][list(data[i].keys())[0]] = -data[i][list(data[i].keys())[0]]

        if "rolling" in request.data.keys() and request.data["rolling"]:
            data = self.rolling_mean(data)

        return Response({"success": True, "length": len(data),
                         "data": data},
                        status=status.HTTP_200_OK)


class GetGlobeData(views.APIView):
    """
    return data for the landing page globe, take in a date range
    """

    def post(self, request):
        try:
            delta = timedelta(days=int(request.data['timedelta']))
            end = datetime.now()
            start = end - delta
            dates = (start, end)
        except BaseException:
            delta = timedelta(days=365)
            end = datetime.now()
            start = end - delta
            dates = (start, end)

        try:
            scenario = request.data["scenario"]
        except BaseException:
            scenario = 'none'

        data = get_count_per_country(scenario, dates)

        df = pd.DataFrame(data, columns=['source_country', 'storycount'])
        df = df[df['source_country'] != '']
        df = df[df['source_country'] != 'U']
        df = df[df['source_country'] != 'GH']

        df['alpha_3'] = df.source_country.map(
            Country.get_iso3_country_code_fuzzy).map(
            lambda x: x[0])

        output = df.groupby('alpha_3').sum().to_dict('index')
        return Response({"success": True, "data": output})
