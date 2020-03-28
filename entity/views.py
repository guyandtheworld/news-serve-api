from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework import views
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from apis.models.users import DashUser, Portfolio
from apis.models.entity import Entity
from apis.models.scenario import Scenario
from .utils import get_anchors, get_alias
from .serializers import (EntitySerializer,
                          EntityListSerializer,
                          AliasSerializer)


class EntityInfo(views.APIView):
    """
    # Add anchor information to a Particular Entity
    * Wikipedia
    * Dbpedia
    * LEI

    # Format

        {
            "entity": "<company name>"
        }
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        entity = request.data["entity"]
        if entity:
            data = get_anchors(entity)
            return Response({"success": True, "data": data},
                            status=status.HTTP_200_OK
                            )
        return Response({"success": False},
                        status=status.HTTP_404_NOT_FOUND)


class EntityAlias(views.APIView):
    """
    Auto-fetch Alias for an Entity from Dbpedia

    # Format

    {
        "entity": "<company name>"
    }
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        entity = request.data["entity"]
        if entity:
            data = get_alias(entity)
            return Response({"success": True, "data": data},
                            status=status.HTTP_200_OK)
        return Response({"success": False},
                        status=status.HTTP_404_NOT_FOUND)


class ListPortfolio(views.APIView):
    """
    List all Entities and Alias in the Portfolio of a Particular User

    # Format

    {
        "user": "<USER UUID>",
        "scenario": "<SCENARIO UUID>"
    }
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = get_object_or_404(DashUser, uuid=request.data["user"])
        scenario = get_object_or_404(Scenario, uuid=request.data["scenario"])
        portfolio = Portfolio.objects.filter(userID=user, scenarioID=scenario)

        portfolio_ids = {}
        for p in portfolio:
            portfolio_ids[str(p.entityID.uuid)] = str(p.uuid)

        if len(portfolio) > 0:
            # fetch entity objects in portfolio
            entities = [en.entityID for en in portfolio]
            serializer = EntityListSerializer(entities, many=True)
            data = serializer.data

            # adds portfolio id to the serialized data
            # i didn't have time to learn how to serialize this
            for i in range(len(data)):
                data[i]['portfolio_id'] = portfolio_ids[data[i]["uuid"]]
            return Response({"success": True, "length": len(entities),
                             "data": data},
                            status=status.HTTP_200_OK)
        msg = "no entities in the portfolio"
        return Response({"success": False, "data": msg},
                        status=status.HTTP_404_NOT_FOUND)


class ListScenarioEntities(views.APIView):
    """
    List all Entities and Aliases being Tracked in a Scenario

    # Format

    {
        "scenario": "<SCENARIO UUID>"
    }
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        scenario = get_object_or_404(Scenario, uuid=request.data["scenario"])
        entities = Entity.objects.filter(scenarioID=scenario)

        if len(entities) > 0:
            # fetch entity objects in portfolio
            serializer = EntityListSerializer(entities, many=True)
            return Response({"success": True, "length": len(entities),
                             "data": serializer.data},
                            status=status.HTTP_200_OK)
        msg = "no entities in the scenario"
        return Response({"success": False, "data": msg})


class AddToPortfolio(views.APIView):
    """
    Add Entity (multiple) to the Portfolio of a User

    {
        "user": "<USER UUID>",
        "scenario": "<SCENARIO UUID>",
        "entity": [<ENTITY UUIDs>]
    }
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):

        # if entity exists in portfolio, do not add
        user = get_object_or_404(DashUser, uuid=request.data["user"])
        scenario = get_object_or_404(Scenario,
                                     uuid=request.data["scenario"])

        portfolio = Portfolio.objects.filter(userID=user,
                                             scenarioID=scenario)
        entities = [en.entityID for en in portfolio]

        portfolio_uuids = []
        for entid in request.data["entity"]:
            entity = get_object_or_404(Entity, uuid=entid)

            # check if entity exists in portfolio
            if entity not in entities:
                obj = Portfolio.objects.create(userID=user,
                                               scenarioID=scenario,
                                               entityID=entity)
                obj.save()
                portfolio_uuids.append(obj.uuid)

        return Response(
            {"success": True, "portfolio_id": portfolio_uuids},
            status=status.HTTP_201_CREATED
        )

    def delete(self, request):
        portfolio_ids = request.data["portfolio_ids"]
        for portfolio_id in portfolio_ids:
            portfolio = Portfolio.objects.get(uuid=portfolio_id)
            portfolio.delete()
        return Response(
            {"success": True},
            status=status.HTTP_200_OK
        )


class AddEntity(views.APIView):
    """
    End-point to create entity.

    # Format
    {
        "name": "CPC Corp",
        "lei": "969500Y9EJECL9E0KM90",
        "dbpediaResource": "http://dbpedia.org/page/Deloitte",
        "wikiResource": "https://en.wikipedia.org/wiki/Deloitte",
        "manualEntry": true,
        "entityType": "company",
        "scenarioID": "<SCENARIO UUID>"
    }
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        entity_serializer = EntitySerializer(data=request.data)
        if entity_serializer.is_valid():

            scenario = get_object_or_404(Scenario,
                                         uuid=request.data["scenarioID"])
            entity = Entity.objects.filter(scenarioID=scenario,
                                           name=request.data["name"])

            # if entity exists in database, just add it to portfolio
            if entity:
                msg = "given entity exists in database"
                return Response({"success": False, "data": msg})
            else:
                entity = entity_serializer.save()
                return Response(
                    {"success": True, "entity_uuid": entity.uuid},
                    status=status.HTTP_201_CREATED
                )
        msg = "no given user or scenario or entity exists"
        return Response({"success": False, "data": msg},
                        status=status.HTTP_404_NOT_FOUND)


class AddAlias(views.APIView):
    """
    Create Alias - You can add multiple Aliases

    # Format

    [{
        "name": "<ENTITY NAME>",
        "entityID": "<ENTITY UUID>"
    }]
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        alias_serializer = AliasSerializer(data=request.data, many=True)
        if alias_serializer.is_valid():
            alias = alias_serializer.save()
            alias_uuid = []
            for obj in alias:
                alias_uuid.append(obj.uuid)
            return Response(
                {"success": True, "alias_uuid": alias_uuid},
                status=status.HTTP_201_CREATED
            )
        msg = "no given user or scenario or entity exists"
        return Response({"success": False, "data": msg},
                        status=status.HTTP_404_NOT_FOUND)
