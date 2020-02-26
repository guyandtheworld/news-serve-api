import json

from datetime import datetime, timedelta
from django.shortcuts import render
from django.core import serializers
from rest_framework import views
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from apis.models.users import DashUser, Portfolio
from apis.models.scenario import Scenario
from apis.models.story import Story
from apis.models.entity import Entity

from .utils import score_in_bulk

DAYS = 30


class GenericGET(views.APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response("Send POST request with JSON object with the correct key")

    def getSingleObjectFromPOST(self, request, key, column, ModelName):
        json_data = json.loads(request.body.decode("utf-8"))
        if key in json_data:
            data = json_data[key]
            obj = ModelName.objects.filter(**{column: data}).first()
            if obj is None:
                return False
            return obj
        return False

    def getManyObjectsFromPOST(self, request, key, column, ModelName):
        if key in request.data:
            data = request.data[key]
            obj = ModelName.objects.filter(**{column: data})
            if obj is None:
                return False
            return obj
        return False


class GetPortfolio(GenericGET):
    """
    generate feed of news for all companies in a user's portfolio
    """

    def post(self, request):
        user = self.getSingleObjectFromPOST(request, "uuid", "uuid", DashUser)
        scenario = self.getSingleObjectFromPOST(
            request, "scenario", "uuid", Scenario)
        if user and scenario:
            query = """
                        select * from public.apis_entity as2 where uuid in
                        (
                        select "entityID_id" from public.apis_portfolio
                        where "userID_id" = '{}'
                        and "scenarioID_id" = '{}'
                        )
                    """
            portfolio = Entity.objects.raw(
                query.format(user.uuid, scenario.uuid))

            if len(portfolio) == 0:
                message = "no companies in portfolio"
                return Response({"success": True, "data": message})

            # fetch articles based on portfolio and
            # all the articles of the required companies
            # which are from the past 6 month and that's active
            start_date = datetime.now() - timedelta(days=DAYS)
            entity_ids = [str(c.uuid) for c in portfolio]

            ids_str = "', '".join(entity_ids)

            query = """
                    select distinct unique_hash, stry.uuid,
                    title, stry.url, search_keyword,
                    published_date, internal_source, "domain",
                    entry_created, "language", source_country,
                    raw_file_source, "entityID_id"
                    FROM public.apis_story as stry
                    inner join
                    (select * from apis_storybody as2 where
                    status_code = 200) as stby
                    on stry.uuid = stby."storyID_id"
                    and "language" in ('english', 'US')
                    and "entityID_id" in ('{}')
                    and published_date > '{}'
                    """
            stories = Story.objects.raw(query.format(ids_str, str(start_date)))

            if len(stories) == 0:
                message = "no articles found"
                return Response({"success": True, "message": message})

            serialized_stories = score_in_bulk(stories)

            return Response({"success": True,
                             "samples": len(serialized_stories),
                             "data": serialized_stories})
        message = "user or scenario doesn't exist"
        return Response({"success": False, "message": message})
