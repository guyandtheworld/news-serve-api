import json

from django.db.models import Q
from rest_framework import views
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from apis.models.users import DashUser
from apis.models.scenario import Scenario, Bucket
from apis.models.entity import Entity

from .sql import (portfolio_score, bucket_score,
                  entity_bucket_score, portfolio_sentiment,
                  portfolio_count)
from .utils import (get_gross_entity_score,
                    get_gross_bucket_scores,
                    get_gross_sentiment_scores)


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


class GetPortfolioScore(GenericGET):
    """
    generate score for a user's portfolio
    """

    def post(self, request):
        user = self.getSingleObjectFromPOST(request, "user", "uuid", DashUser)
        scenario = self.getSingleObjectFromPOST(
            request, "scenario", "uuid", Scenario)

        # check if user is subscribed to the scenario
        if user.defaultScenario != scenario:
            message = "user is not subscribed to the scenario"
            return Response({"success": False, "message": message})


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

            entity_ids = [str(c.uuid) for c in portfolio]
            entity_scores = portfolio_score(entity_ids, scenario.uuid)

            # if no scores return 0
            scores = []
            if len(entity_scores) == 0:
                obj = {}
                for entity in portfolio:
                    obj["uuid"] = entity.uuid
                    obj["name"] = entity.name
                    obj["gross_entity_score"] = 0
                    scores.append(obj)
                return Response({"success": True,
                                 "samples": len(scores),
                                 "data": scores})

            scores = get_gross_entity_score(entity_scores)

            return Response({"success": True,
                             "samples": len(scores),
                             "data": scores})

        message = "user or scenario doesn't exist"
        return Response({"success": False, "message": message})


class GetSentiment(GenericGET):
    """
    generate sentiment for a user's portfolio
    """

    def post(self, request):
        user = self.getSingleObjectFromPOST(request, "user", "uuid", DashUser)
        scenario = self.getSingleObjectFromPOST(
            request, "scenario", "uuid", Scenario)

        # check if user is subscribed to the scenario
        if user.defaultScenario != scenario:
            message = "user is not subscribed to the scenario"
            return Response({"success": False, "message": message})

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

            entity_ids = [str(c.uuid) for c in portfolio]
            entity_scores = portfolio_sentiment(entity_ids)

            scores = get_gross_sentiment_scores(entity_scores)

            return Response({"success": True,
                             "samples": len(scores),
                             "data": scores})

        message = "user or scenario doesn't exist"
        return Response({"success": False, "message": message})


class GetNewsCount(GenericGET):
    """
    generate sentiment for a user's portfolio
    """

    def post(self, request):
        user = self.getSingleObjectFromPOST(request, "user", "uuid", DashUser)
        scenario = self.getSingleObjectFromPOST(
            request, "scenario", "uuid", Scenario)

        # check if user is subscribed to the scenario
        if user.defaultScenario != scenario:
            message = "user is not subscribed to the scenario"
            return Response({"success": False, "message": message})

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

            entity_ids = [str(c.uuid) for c in portfolio]
            counts = portfolio_count(entity_ids)

            return Response({"success": True,
                             "samples": len(counts),
                             "data": counts})

        message = "user or scenario doesn't exist"
        return Response({"success": False, "message": message})


class GetBucketScore(GenericGET):
    """
    generate score for all buckets of Scenario
    """

    def post(self, request):
        user = self.getSingleObjectFromPOST(request, "user", "uuid", DashUser)
        scenario = self.getSingleObjectFromPOST(
            request, "scenario", "uuid", Scenario)

        # check if user is subscribed to the scenario
        if user.defaultScenario != scenario:
            message = "user is not subscribed to the scenario"
            return Response({"success": False, "message": message})

        if user and scenario:

            # get all buckets except the other model
            buckets = Bucket.objects.filter(~Q(model_label = "other"),
                                            scenarioID=str(scenario.uuid))

            if len(list(buckets)) == 0:
                message = "no buckets in this scenario"
                return Response({"success": True, "data": message})

            bucket_ids = [str(b.uuid) for b in buckets]
            bucket_scores = bucket_score(bucket_ids, scenario.uuid)

            # if no scores return 0
            scores = []
            if len(bucket_scores) == 0:
                obj = {}
                for bucket in buckets:
                    obj["uuid"] = bucket.uuid
                    obj["name"] = bucket.name
                    obj["score"] = 0
                    scores.append(obj)
                return Response({"success": True,
                                 "samples": len(scores),
                                 "data": scores})

            scores = get_gross_bucket_scores(bucket_scores)

            return Response({"success": True,
                             "samples": len(scores),
                             "data": scores})

        message = "user or scenario doesn't exist"
        return Response({"success": False, "message": message})


class GetEntityBucketScore(GenericGET):
    """
    generate score for all buckets of Scenario
    """

    def post(self, request):
        user = self.getSingleObjectFromPOST(request, "user", "uuid", DashUser)
        scenario = self.getSingleObjectFromPOST(
            request, "scenario", "uuid", Scenario)
        entity = self.getSingleObjectFromPOST(
            request, "entity", "uuid", Entity)


        # check if user is subscribed to the scenario
        if user.defaultScenario != scenario:
            message = "user is not subscribed to the scenario"
            return Response({"success": False, "message": message})

        if user and scenario and entity:

            # get all buckets except the other model
            buckets = Bucket.objects.filter(~Q(model_label = "other"),
                                            scenarioID=str(scenario.uuid))

            if len(list(buckets)) == 0:
                message = "no buckets in this scenario"
                return Response({"success": True, "data": message})

            entity_scores = entity_bucket_score(entity.uuid, scenario.uuid)

            # if no scores return 0
            scores = []
            if len(entity_scores) == 0:
                obj = {}
                for bucket in buckets:
                    obj["uuid"] = bucket.uuid
                    obj["name"] = bucket.name
                    obj["score"] = 0
                    scores.append(obj)
                return Response({"success": True,
                                 "samples": len(scores),
                                 "data": scores})

            scores = get_gross_bucket_scores(entity_scores)

            return Response({"success": True,
                             "samples": len(scores),
                             "data": scores})

        message = "user or scenario or entity doesn't exist"
        return Response({"success": False, "message": message})