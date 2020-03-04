import json

from rest_framework import views
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from apis.models.users import DashUser
from apis.models.scenario import Scenario, Bucket
from apis.models.entity import Entity

from .sql import portfolio_score
from .utils import hotness, get_gross_entity_score


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


class GetPortfolioScore(GenericGET):
    """
    generate score for a user's portfolio
    """

    def post(self, request):
        user = self.getSingleObjectFromPOST(request, "user", "uuid", DashUser)
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

            entity_ids = [str(c.uuid) for c in portfolio]
            entity_scores = portfolio_score(entity_ids)

            scores = get_gross_entity_score(entity_scores)

            return Response({"success": True,
                             "samples": len(scores),
                             "data": scores})

        message = "user or scenario doesn't exist"
        return Response({"success": False, "message": message})
