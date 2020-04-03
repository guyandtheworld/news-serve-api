import json

from django.shortcuts import get_object_or_404
from rest_framework import views
from rest_framework import status
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from apis.models.users import DashUser
from apis.models.scenario import Scenario, Bucket
from apis.models.entity import Entity, StoryEntityRef

from auto.utils import get_scenario_entity_count

from .utils import score_in_bulk, attach_story_entities
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

    def getEntitiesFromAuto(self, request, scenario_id):
        if 'n_entities' in request.data:
            n_entities = request.data['n_entities']
        else:
            n_entities = 20
        if 'type' in request.data:
            type_id = request.data['type']
        else:
            type_id = None
        auto_entities = get_scenario_entity_count(scenario_id, type_id, n_entities)
        entity_ids = [str(ent['entityID_id']) for ent in auto_entities]
        return entity_ids

    def getMode(self, request):
        if "mode" in request.data:
            mode = request.data["mode"]
        else:
            mode = "portfolio"
        return mode


class GetPortfolio(GenericGET):
    """
    Generate feed of news for all companies in a user's portfolio, or all
    entities defined in the auto entities. Pass flag "auto" or "portfolio" for
    each case.
    """

    def post(self, request):
        user = self.getSingleObjectFromPOST(request, "user", "uuid", DashUser)
        scenario = self.getSingleObjectFromPOST(
            request, "scenario", "uuid", Scenario)
        mode = self.getMode(request)

        # check if user is subscribed to the scenario
        if user and scenario:
            if mode == 'portfolio':
                if user:
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
            elif mode == 'auto':
                entity_ids = self.getEntitiesFromAuto(request, scenario.uuid)

            # fetch portfolio
            stories = user_portfolio(entity_ids, mode)

            if len(stories) == 0:
                message = "no articles found"
                return Response({"success": True, "message": message})

            stories = score_in_bulk(stories, mode=mode)
            processed_stories = attach_story_entities(stories)

            return Response({"success": True,
                             "samples": len(processed_stories),
                             "data": processed_stories},
                            status=status.HTTP_200_OK)
        message = "user or scenario doesn't exist"
        return Response({"success": False, "message": message},
                        status=status.HTTP_404_NOT_FOUND)


class GetEntity(GenericGET):
    """
    Generate feed of a particular company. Pass flag "auto" or "portfolio" for
    each case.
    """

    def post(self, request):
        mode = self.getMode(request)
        if mode == 'portfolio':
            entity = get_object_or_404(Entity, uuid=request.data["entity"])
        else:
            entity = get_object_or_404(StoryEntityRef, uuid=request.data["entity"])

        if entity:
            stories = user_entity(entity.uuid, mode)

            if len(stories) == 0:
                message = "no articles found"
                return Response({"success": True, "message": message})

            stories = score_in_bulk(stories, mode=mode)
            processed_stories = attach_story_entities(stories)

            return Response({"success": True,
                             "samples": len(processed_stories),
                             "data": processed_stories},
                            status=status.HTTP_200_OK)

        message = "user or entity doesn't exist"
        return Response({"success": False, "message": message},
                        status=status.HTTP_404_NOT_FOUND)


class GetBucket(GenericGET):
    """
    Generate feed of a particular bucket based on
    BucketScore table. Pass flag "auto" or "portfolio" for
    each case.
    """

    def post(self, request):
        user = self.getSingleObjectFromPOST(request, "user", "uuid", DashUser)
        bucket = self.getSingleObjectFromPOST(request, "bucket", "uuid", Bucket)
        mode = self.getMode(request)

        if user and bucket:
            if user.defaultScenario != bucket.scenarioID:
                message = "you're not subscribed to this scenario'"
                return Response({"success": False, "message": message})
            if mode == 'portfolio':
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
            elif mode == 'auto':
                entity_ids = self.getEntitiesFromAuto(
                    request, bucket.scenarioID.uuid)

            stories = user_bucket(bucket.uuid, entity_ids,
                                  bucket.scenarioID.uuid, mode)

            if len(stories) == 0:
                message = "no articles found"
                return Response({"success": True, "message": message})

            stories = score_in_bulk(stories, bucket=True, mode=mode)
            processed_stories = attach_story_entities(stories)

            return Response({"success": True,
                             "samples": len(processed_stories),
                             "data": processed_stories},
                            status=status.HTTP_200_OK)

        message = "user or bucket doesn't exist"
        return Response({"success": False, "message": message},
                        status=status.HTTP_404_NOT_FOUND)


class GetBucketEntity(GenericGET):
    """
    Generate feed of a particular entity based on a bucket.
    Pass flag "auto" or "portfolio" for each case.
    """

    def post(self, request):
        user = self.getSingleObjectFromPOST(request, "user", "uuid", DashUser)
        bucket = self.getSingleObjectFromPOST(request, "bucket", "uuid", Bucket)
        mode = self.getMode(request)

        if mode == 'portfolio':
            entity = get_object_or_404(Entity, uuid=request.data["entity"])
        else:
            entity = get_object_or_404(StoryEntityRef, uuid=request.data["entity"])

        if bucket and entity:
            if user.defaultScenario != bucket.scenarioID:
                message = "you're not subscribed to this scenario'"
                return Response({"success": False, "message": message})

            if mode == "portfolio" and entity.scenarioID != bucket.scenarioID:
                message = "this entity is not tracked under this scenario'"
                return Response({"success": False, "message": message})

            stories = user_entity_bucket(
                bucket.uuid, entity.uuid, bucket.scenarioID.uuid, mode)

            if len(stories) == 0:
                message = "no articles found"
                return Response({"success": True, "message": message})

            stories = score_in_bulk(stories, bucket=True, mode=mode)
            processed_stories = attach_story_entities(stories)

            return Response({"success": True,
                             "samples": len(processed_stories),
                             "data": processed_stories},
                            status=status.HTTP_200_OK)

        message = "user or bucket doesn't exist"
        return Response({"success": False, "message": message},
                        status=status.HTTP_404_NOT_FOUND)
