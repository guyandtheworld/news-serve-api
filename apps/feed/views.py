import json


from django.shortcuts import get_object_or_404
from django.db import connection
from datetime import datetime, timedelta

from rest_framework import views
from rest_framework import status
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from apis.models.users import DashUser
from apis.models.scenario import Scenario, Bucket
from apis.models.entity import Entity, StoryEntityRef

from auto.utils import get_scenario_entity_count

from .sql import (user_portfolio,
                  user_entity,
                  user_bucket,
                  user_entity_bucket)


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

    def getEntitiesFromAuto(self, request, scenario_id, dates):
        if 'n_entities' in request.data:
            n_entities = request.data['n_entities']
        else:
            n_entities = 20
        if 'type' in request.data:
            type_id = request.data['type']
        else:
            type_id = None
        auto_entities = get_scenario_entity_count(
            scenario_id, type_id, n_entities, dates)
        entity_ids = [str(ent['entityID_id']) for ent in auto_entities]
        return entity_ids

    def getMode(self, request):
        if "mode" in request.data:
            mode = request.data["mode"]
        else:
            mode = "portfolio"
        return mode

    def getPortfolio(self, user, scenario):
        """
        Return the entities in user's portfolio
        """
        query = """
                select uuid from public.apis_entity where uuid in
                (
                select "entityID_id" from public.apis_portfolio
                where "userID_id" = '{}'
                and "scenarioID_id" = '{}')
                """.format(str(user.uuid), str(scenario.uuid))

        with connection.cursor() as cursor:
            cursor.execute(query)
            rows = [
                str(row[0]) for row in cursor.fetchall()
            ]
        return rows

    def getPage(self, request):
        """
        Get page number of the feed.
        """
        if "page" in request.data:
            page = request.data["page"]
        else:
            page = 1
        return page

    def getDates(self, request):
        """
        Get dates from the request
        """
        date_format = '%Y-%m-%d'
        decay = "FALSE"

        data = request.data.keys()

        if 'start_date' in data and 'end_date' in data:
            start_date = datetime.strptime(request.data['start_date'], date_format)
            end_date = datetime.strptime(request.data['end_date'], date_format)
        elif 'start_date' in data:
            start_date = datetime.strptime(request.data['start_date'], date_format)
            end_date = datetime.now()
        else:
            default_timeperiod = 7
            end_date = datetime.now()
            start_date = end_date - timedelta(days=default_timeperiod)

        if start_date > (datetime.now() - timedelta(days=15)):
            decay = "TRUE"

        return start_date, end_date, decay


class GetPortfolio(GenericGET):

    """
    Generate feed of news for all companies in a user's portfolio, or all
    entities defined in the auto entities. Pass flag "auto" or "portfolio" for
    each case.
    """

    def post(self, request):
        user = self.getSingleObjectFromPOST(request, "user", "uuid", DashUser)
        scenario = self.getSingleObjectFromPOST(request, "scenario", "uuid", Scenario)  # noqa
        mode = self.getMode(request)
        dates = self.getDates(request)
        page = self.getPage(request)

        # check if user is subscribed to the scenario
        if user and scenario:
            if mode == 'portfolio':
                entity_ids = self.getPortfolio(user, scenario)
                if len(entity_ids) == 0:
                    message = "no companies in portfolio"
                    return Response({"success": True, "data": message})
            elif mode == 'auto':
                entity_ids = self.getEntitiesFromAuto(request, scenario.uuid, dates)
                if len(entity_ids) == 0:
                    message = "no entities in portfolio"
                    return Response({"success": True, "data": message})

            # fetch portfolio
            stories = user_portfolio(entity_ids, scenario.uuid, dates, mode, page)

            if len(stories) == 0:
                message = "no articles found"
                return Response({"success": True, "message": message},
                                status=status.HTTP_200_OK)

            return Response({"success": True,
                             "samples": len(stories),
                             "data": stories},
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
        user = self.getSingleObjectFromPOST(request, "user", "uuid", DashUser)
        entity = self.getSingleObjectFromPOST(request, "entity", "uuid", Entity)
        scenario = self.getSingleObjectFromPOST(request, "scenario", "uuid", Scenario) # noqa
        mode = self.getMode(request)
        dates = self.getDates(request)
        page = self.getPage(request)
        search_keyword = None

        if mode == 'keyword':
            search_keyword = request.data['search_keyword']
            if search_keyword not in entity.keywords:
                message = "keyword doesn't exist"
                return Response({"success": False, "message": message})
        if mode == 'portfolio':
            entity = get_object_or_404(Entity, uuid=request.data["entity"])
        else:
            entity = get_object_or_404(StoryEntityRef, uuid=request.data["entity"])

        if entity:
            stories = user_entity(entity.uuid, scenario.uuid, dates, mode, page, search_keyword)

            if len(stories) == 0:
                message = "no articles found"
                return Response({"success": True, "message": message},
                                status=status.HTTP_200_OK)
            return Response({"success": True,
                             "samples": len(stories),
                             "data": stories},
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
        scenario = self.getSingleObjectFromPOST(request, "scenario", "uuid", Scenario) # noqa
        mode = self.getMode(request)
        dates = self.getDates(request)
        page = self.getPage(request)

        if bucket.scenarioID != scenario:
            message = "Bucket does not exist in Scenario."
            return Response({"success": False, "message": message},
                            status=status.HTTP_404_NOT_FOUND)

        if user and bucket:
            if mode == 'portfolio':
                entity_ids = self.getPortfolio(user, scenario)
            elif mode == 'auto':
                entity_ids = self.getEntitiesFromAuto(
                    request, bucket.scenarioID.uuid, dates)

            # if no entities exists, return
            if len(entity_ids) == 0:
                message = "no entities found"
                return Response({"success": False, "message": message},
                                status=status.HTTP_404_NOT_FOUND)

            stories = user_bucket(bucket.uuid, entity_ids,
                                  scenario.uuid, dates, mode, page)

            if len(stories) == 0:
                message = "no articles found"
                return Response({"success": True, "message": message},
                                status=status.HTTP_200_OK)

            return Response({"success": True,
                             "samples": len(stories),
                             "data": stories},
                            status=status.HTTP_200_OK)

        message = "User or Bucket doesn't exist."
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
        scenario = self.getSingleObjectFromPOST(request, "scenario", "uuid", Scenario) # noqa
        mode = self.getMode(request)
        dates = self.getDates(request)
        page = self.getPage(request)

        if bucket.scenarioID != scenario:
            message = "Bucket does not exist in Scenario."
            return Response({"success": False, "message": message},
                            status=status.HTTP_404_NOT_FOUND)

        if mode == 'portfolio':
            entity = get_object_or_404(Entity, uuid=request.data["entity"])
        else:
            entity = get_object_or_404(StoryEntityRef, uuid=request.data["entity"])

        if bucket and entity:
            stories = user_entity_bucket(
                bucket.uuid, entity.uuid, scenario.uuid, dates, mode, page)

            if len(stories) == 0:
                message = "no articles found"
                return Response({"success": True, "message": message},
                                status=status.HTTP_200_OK)

            return Response({"success": True,
                             "samples": len(stories),
                             "data": stories},
                            status=status.HTTP_200_OK)

        message = "user or bucket doesn't exist"
        return Response({"success": False, "message": message},
                        status=status.HTTP_404_NOT_FOUND)
