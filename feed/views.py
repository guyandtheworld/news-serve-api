import json
import pandas as pd

from rest_framework import views
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from apis.models.users import DashUser
from apis.models.scenario import Scenario, Bucket
from apis.models.entity import Entity

from .utils import score_in_bulk,attach_story_entities
from .sql import user_portfolio, user_entity, user_bucket, user_entity_bucket


class GenericGET(views.APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

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

        # check if user is subscribed to the scenario

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

            portfolio = [c for c in portfolio]

            if len(portfolio) == 0:
                message = "no companies in portfolio"
                return Response({"success": True, "data": message})

            # fetch articles based on portfolio and
            # all the articles of the required companies
            # which are from the past 6 month and that's active
            entity_ids = [str(c.uuid) for c in portfolio]

            stories = user_portfolio(entity_ids)

            if len(stories) == 0:
                message = "no articles found"
                return Response({"success": True, "message": message})

            processed_stories = attach_story_entities(score_in_bulk(stories))

            return Response({"success": True,
                             "samples": len(processed_stories),
                             "data": processed_stories})
        message = "user or scenario doesn't exist"
        return Response({"success": False, "message": message})


class GetEntity(GenericGET):
    """
    generate feed of a particular company
    """

    def post(self, request):
        user = self.getSingleObjectFromPOST(
            request, "user_uuid", "uuid", DashUser)
        entity = self.getSingleObjectFromPOST(
            request, "company_uuid", "uuid", Entity)
        if entity:
            stories = user_entity(entity.uuid)

            if len(stories) == 0:
                message = "no articles found"
                return Response({"success": True, "message": message})

            processed_stories = attach_story_entities(score_in_bulk(stories))


            return Response({"success": True,
                             "samples": len(processed_stories),
                             "data": processed_stories})

        message = "user or entity doesn't exist"
        return Response({"success": False, "message": message})


class GetBucket(GenericGET):
    """
    generate feed of a particular bucket based on
    BucketScore table
    """

    def post(self, request):
        user = self.getSingleObjectFromPOST(
            request, "user_uuid", "uuid", DashUser)
        bucket = self.getSingleObjectFromPOST(
            request, "bucket_uuid", "uuid", Bucket)

        if user and bucket:
            if user.defaultScenario != bucket.scenarioID:
                message = "you're not subscribed to this scenario'"
                return Response({"success": False, "message": message})

            query = """
                        select * from public.apis_entity as2 where uuid in
                        (
                        select "entityID_id" from public.apis_portfolio
                        where "userID_id" = '{}'
                        and "scenarioID_id" = '{}'
                        )
                    """
            portfolio = Entity.objects.raw(
                query.format(user.uuid, bucket.scenarioID.uuid))

            portfolio = [c for c in portfolio]

            if len(portfolio) == 0:
                message = "no companies in portfolio"
                return Response({"success": True, "data": message})

            entity_ids = [str(c.uuid) for c in portfolio]
            stories = user_bucket(bucket.uuid, entity_ids, bucket.scenarioID.uuid)

            if len(stories) == 0:
                message = "no articles found"
                return Response({"success": True, "message": message})

            processed_stories = attach_story_entities(score_in_bulk(stories, bucket=True))

            return Response({"success": True,
                             "samples": len(processed_stories),
                             "data": processed_stories})

        message = "user or bucket doesn't exist"
        return Response({"success": False, "message": message})


class GetBucketEntity(GenericGET):
    """
    generate feed of a particular entity based on a bucket
    """

    def post(self, request):
        user = self.getSingleObjectFromPOST(
            request, "user_uuid", "uuid", DashUser)
        bucket = self.getSingleObjectFromPOST(
            request, "bucket_uuid", "uuid", Bucket)
        entity = self.getSingleObjectFromPOST(
            request, "entity_uuid", "uuid", Entity)

        if user and bucket and entity:
            if user.defaultScenario != bucket.scenarioID:
                message = "you're not subscribed to this scenario'"
                return Response({"success": False, "message": message})

            if entity.scenarioID != bucket.scenarioID:
                message = "this entity is not tracked under this scenario'"
                return Response({"success": False, "message": message})

            stories = user_entity_bucket(bucket.uuid, entity.uuid, bucket.scenarioID.uuid)

            if len(stories) == 0:
                message = "no articles found"
                return Response({"success": True, "message": message})

            processed_stories = attach_story_entities(score_in_bulk(stories, bucket=True))

            return Response({"success": True,
                             "samples": len(processed_stories),
                             "data": processed_stories})

        message = "user or bucket doesn't exist"
        return Response({"success": False, "message": message})
