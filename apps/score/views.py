import json

from django.db.models import Q
from rest_framework import status
from rest_framework import views
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from apis.models.users import DashUser
from apis.models.scenario import Scenario, Bucket
from apis.models.entity import Entity, StoryEntityRef
from auto.utils import get_scenario_entity_count

from .sql import (portfolio_score, bucket_score,
                  entity_bucket_score, portfolio_sentiment,
                  portfolio_count)
from .utils import (get_gross_entity_score,
                    get_gross_bucket_scores,
                    get_gross_sentiment_scores)
from apis.utils import extract_timeperiod


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
        entity_obj = StoryEntityRef.objects.filter(uuid__in=entity_ids)
        return entity_obj, entity_ids

    def getPortfolio(self, user_uuid, scenario_uuid):
        """
        Fetch a portfolio of a particular user
        """
        query = """
                    select * from public.apis_entity as2 where uuid in
                    (
                    select "entityID_id" from public.apis_portfolio
                    where "userID_id" = '{}'
                    and "scenarioID_id" = '{}'
                    )
                """

        portfolio = Entity.objects.raw(
            query.format(user_uuid, scenario_uuid))

        portfolio = [c for c in portfolio]
        return portfolio

    def getScores(self, entity_scores, portfolio, entity_ids, metric, func):
        """
        Normalize the scores and add type to the entities.
        """

        scores = func(entity_scores)

        # check entities without scores
        entity_obj = {str(x.uuid): x for x in portfolio}
        not_scored = list(set(entity_ids) -
                          set([str(score["uuid"]) for score in scores]))
        for uuid in not_scored:
            entity = entity_obj[uuid]
            obj = {}
            obj["uuid"] = entity.uuid
            obj["name"] = entity.name
            obj["type"] = entity.typeID.name
            obj["wikipedia"] = entity.wikipedia
            obj[metric] = 0.0
            scores.append(obj)

        return scores


class GetPortfolioScore(GenericGET):
    """
    generate score for a user's portfolio
    """

    def post(self, request):
        user = self.getSingleObjectFromPOST(request, "user", "uuid", DashUser)
        scenario = self.getSingleObjectFromPOST(
            request, "scenario", "uuid", Scenario)
        dates = extract_timeperiod(request)

        if "mode" in request.data:
            mode = request.data["mode"]
        else:
            mode = "portfolio"

        if user and scenario:
            portfolio = []
            entity_ids = []

            # check if user is subscribed to the scenario
            if user.defaultScenario != scenario:
                message = "user is not subscribed to the scenario"
                return Response({"success": False, "message": message})

            if mode == "portfolio":

                # fetch the portfolio of a particular user
                portfolio = self.getPortfolio(user.uuid, scenario.uuid)
                if len(portfolio) == 0:
                    message = "no companies in portfolio"
                    return Response({"success": True, "data": message},
                                    status=status.HTTP_404_NOT_FOUND)

                entity_ids = [str(c.uuid) for c in portfolio]
            elif mode == "auto":
                portfolio, entity_ids = self.getEntitiesFromAuto(
                    request, scenario.uuid, dates)

                if len(entity_ids) == 0:
                    message = "no entities found"
                    return Response({"success": False, "message": message},
                                    status=status.HTTP_404_NOT_FOUND)

            entity_scores = portfolio_score(entity_ids, scenario.uuid, dates)
            scores = self.getScores(entity_scores, portfolio, entity_ids,
                                    metric="gross_entity_score",
                                    func=get_gross_entity_score)

            return Response({"success": True,
                             "samples": len(scores),
                             "data": scores},
                            status=status.HTTP_200_OK)

        message = "user or scenario doesn't exist"
        return Response({"success": False, "message": message},
                        status=status.HTTP_404_NOT_FOUND)


class GetSentiment(GenericGET):
    """
    generate sentiment for a user's portfolio
    """

    def post(self, request):
        user = self.getSingleObjectFromPOST(request, "user", "uuid", DashUser)
        scenario = self.getSingleObjectFromPOST(
            request, "scenario", "uuid", Scenario)
        dates = extract_timeperiod(request)
        # check if user is subscribed to the scenario

        if "mode" in request.data:
            mode = request.data["mode"]
        else:
            mode = "portfolio"

        if user and scenario:
            portfolio = []
            entity_ids = []

            if user.defaultScenario != scenario:
                message = "user is not subscribed to the scenario"
                return Response({"success": False, "message": message})

            if mode == "portfolio":

                portfolio = self.getPortfolio(user.uuid, scenario.uuid)

                if len(portfolio) == 0:
                    message = "no companies in portfolio"
                    return Response({"success": True, "data": message},
                                    status=status.HTTP_404_NOT_FOUND)

                entity_ids = [str(c.uuid) for c in portfolio]
            elif mode == "auto":

                portfolio, entity_ids = self.getEntitiesFromAuto(
                    request, scenario.uuid, dates)

                if len(entity_ids) == 0:
                    message = "no entities found"
                    return Response({"success": False, "message": message},
                                    status=status.HTTP_404_NOT_FOUND)

            entity_scores = portfolio_sentiment(entity_ids, dates, mode)

            scores = self.getScores(entity_scores, portfolio, entity_ids,
                                    metric="sentiment",
                                    func=get_gross_sentiment_scores)

            return Response({"success": True,
                             "samples": len(scores),
                             "data": scores},
                            status=status.HTTP_200_OK)

        message = "user or scenario doesn't exist"
        return Response({"success": False, "message": message},
                        status=status.HTTP_404_NOT_FOUND)


class GetNewsCount(GenericGET):
    """
    generate sentiment for a user's portfolio
    """

    def post(self, request):
        user = self.getSingleObjectFromPOST(request, "user", "uuid", DashUser)
        scenario = self.getSingleObjectFromPOST(
            request, "scenario", "uuid", Scenario)
        dates = extract_timeperiod(request)
        # check if user is subscribed to the scenario

        if "mode" in request.data:
            mode = request.data["mode"]
        else:
            mode = "portfolio"

        if user and scenario:
            portfolio = []
            entity_ids = []

            if user.defaultScenario != scenario:
                message = "user is not subscribed to the scenario"
                return Response({"success": False, "message": message})

            if mode == "portfolio":

                portfolio = self.getPortfolio(user.uuid, scenario.uuid)

                if len(portfolio) == 0:
                    message = "no companies in portfolio"
                    return Response({"success": True, "data": message},
                                    status=status.HTTP_404_NOT_FOUND)

                entity_ids = [str(c.uuid) for c in portfolio]
            elif mode == "auto":
                portfolio, entity_ids = self.getEntitiesFromAuto(
                    request, scenario.uuid, dates)

                if len(entity_ids) == 0:
                    message = "no entities found"
                    return Response({"success": False, "message": message},
                                    status=status.HTTP_404_NOT_FOUND)

            entity_scores = portfolio_count(entity_ids, dates, mode)

            scores = self.getScores(entity_scores, portfolio, entity_ids,
                                    metric="news_count",
                                    func=lambda x: x)

            return Response({"success": True,
                             "samples": len(scores),
                             "data": scores},
                            status=status.HTTP_200_OK)

        message = "user or scenario doesn't exist"
        return Response({"success": False, "message": message},
                        status=status.HTTP_404_NOT_FOUND)


class GetBucketScore(GenericGET):
    """
    generate score for all buckets of Scenario
    """

    def post(self, request):
        user = self.getSingleObjectFromPOST(request, "user", "uuid", DashUser)
        scenario = self.getSingleObjectFromPOST(
            request, "scenario", "uuid", Scenario)
        dates = extract_timeperiod(request)

        if user and scenario:
            # check if user is subscribed to the scenario
            if user.defaultScenario != scenario:
                message = "user is not subscribed to the scenario"
                return Response({"success": False, "message": message})

            # get all buckets except the other model
            buckets = Bucket.objects.filter(~Q(model_label="other"),
                                            scenarioID=str(scenario.uuid))

            if len(list(buckets)) == 0:
                message = "no buckets in this scenario"
                return Response({"success": True, "data": message},
                                status=status.HTTP_404_NOT_FOUND)

            bucket_ids = [str(b.uuid) for b in buckets]
            bucket_scores = bucket_score(bucket_ids, scenario.uuid, dates)

            # if no scores return 0
            scores = []
            if len(bucket_scores) == 0:
                for bucket in buckets:
                    obj = {}
                    obj["uuid"] = bucket.uuid
                    obj["name"] = bucket.name
                    obj["score"] = 0
                    scores.append(obj)
                return Response({"success": True,
                                 "samples": len(scores),
                                 "data": scores},
                                status=status.HTTP_200_OK)

            scores = get_gross_bucket_scores(bucket_scores)

            return Response({"success": True,
                             "samples": len(scores),
                             "data": scores},
                            status=status.HTTP_200_OK)

        message = "user or scenario doesn't exist"
        return Response({"success": False, "message": message},
                        status=status.HTTP_404_NOT_FOUND)


class GetEntityBucketScore(GenericGET):
    """
    generate score for all buckets of Scenario
    """

    def post(self, request):
        user = self.getSingleObjectFromPOST(request, "user", "uuid", DashUser)
        scenario = self.getSingleObjectFromPOST(
            request, "scenario", "uuid", Scenario)
        entity = self.getSingleObjectFromPOST(
            request, "entity", "uuid", StoryEntityRef)
        dates = extract_timeperiod(request)

        if user and scenario and entity:

            # check if user is subscribed to the scenario
            if user.defaultScenario != scenario:
                message = "user is not subscribed to the scenario"
                return Response({"success": False, "message": message})

            # get all buckets except the other model
            buckets = Bucket.objects.filter(~Q(model_label="other"),
                                            scenarioID=str(scenario.uuid))

            if len(list(buckets)) == 0:
                message = "no buckets in this scenario"
                return Response({"success": True, "data": message},
                                status=status.HTTP_404_NOT_FOUND)

            entity_scores = entity_bucket_score(entity.uuid, scenario.uuid, dates)

            # if no scores return 0
            scores = []
            if len(entity_scores) == 0:
                for bucket in buckets:
                    obj = {}
                    obj["uuid"] = bucket.uuid
                    obj["name"] = bucket.name
                    obj["score"] = 0
                    scores.append(obj)
                return Response({"success": True,
                                 "samples": len(scores),
                                 "data": scores},
                                status=status.HTTP_200_OK)

            scores = get_gross_bucket_scores(entity_scores)

            return Response({"success": True,
                             "samples": len(scores),
                             "data": scores},
                            status=status.HTTP_200_OK)

        message = "user or scenario or entity doesn't exist"
        return Response({"success": False, "message": message},
                        status=status.HTTP_404_NOT_FOUND)
