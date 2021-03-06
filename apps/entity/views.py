from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.db import connection

from rest_framework import status
from rest_framework import views
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from apis.models.users import DashUser, Portfolio
from apis.models.entity import Entity, StoryEntityRef
from apis.models.scenario import Scenario
from score.views import GenericGET
from score.sql import portfolio_count
from apis.utils import extract_timeperiod

from .utils import get_anchors, get_alias
from .serializers import (EntitySerializer,
                          EntityListSerializer,
                          StoryEntityRefSerializer)


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
    List all Entities in the Portfolio of a Particular User

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
    List all Entities being Tracked in a Scenario

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
        return Response({"success": False, "data": msg},
                        status=status.HTTP_404_NOT_FOUND
                        )


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
        if "portfolio_ids" not in request.data:
            return Response({"success": False},
                            status=status.HTTP_404_NOT_FOUND)

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
        "entityType": <ENTITY TYPE>,
        "scenarioID": "<SCENARIO UUID>",
        "keywords": "[<List of Keywords>]"
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

    def delete(self, request):

        try:
            entity = request.data["entity"]
        except BaseException:
            msg = "no entity in request"
            return Response({"success": False, "data": msg},
                            status=status.HTTP_404_NOT_FOUND)

        entity = get_object_or_404(Entity,
                                   uuid=entity)

        message = entity.name
        entity.delete()

        return Response(
            {"success": True, "entity": message},
            status=status.HTTP_201_CREATED
        )


class EntityRef(views.APIView):
    """
    CRUD on EntityRef of the Stories
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        entities = StoryEntityRef.objects.filter(render=False)
        serializer = StoryEntityRefSerializer(entities, many=True)
        return Response(
            {"success": True, "result": serializer.data[:100]},
            status=status.HTTP_200_OK
        )

    def put(self, request):
        ent_data = request.data
        for ent in ent_data:
            entity = get_object_or_404(StoryEntityRef, uuid=ent["uuid"])
            serializer = StoryEntityRefSerializer(entity, data=ent,
                                                  partial=True)
            if serializer.is_valid():
                serializer.save()

        return Response({"success": True},
                        status=status.HTTP_200_OK
                        )

    def delete(self, request):
        uuids = request.data
        for uuid in uuids:
            entity_ref = StoryEntityRef.objects.get(uuid=uuid)
            entity_ref.render = False
            entity_ref.save()
        return Response(
            {"success": True},
            status=status.HTTP_200_OK
        )


class EntitySearch(views.APIView):
    """
    Search database for a particular API
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        keyword = request.data["keyword"]
        if len(keyword) < 3:
            msg = "Please provide a better description"
            return Response({"success": False, "data": msg},
                            status=status.HTTP_406_NOT_ACCEPTABLE)

        # return entity where wikipedia link is present
        entities = StoryEntityRef.objects.filter(
            name__icontains=keyword).exclude(wikipedia="")
        serializer = StoryEntityRefSerializer(entities, many=True)
        return Response(
            {"success": True, "result": serializer.data},
            status=status.HTTP_200_OK
        )


class ManageEntity(GenericGET):
    """
    Return the latest or the most popular
    entities in the database based on the
    filter
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        scenario = self.getSingleObjectFromPOST(
            request, "scenario", "uuid", Scenario)

        dates = extract_timeperiod(request)

        if request.data["filter"] == "latest":

            entities = StoryEntityRef.objects.filter(
                render=True).order_by('-created_at')

            paginator = Paginator(entities, 50)
            page = request.GET.get('page')

            try:
                entities = paginator.page(page)
            except Exception:
                entities = paginator.page(1)

            entity_ids = [str(entity.uuid) for entity in entities]

            entity_scores = portfolio_count(entity_ids, dates, mode="auto")

            scores = self.getScores(entity_scores, entities, entity_ids,
                                    metric="news_count",
                                    func=lambda x: x)
        elif request.data["filter"] == "popular":
            portfolio, entity_ids = self.getEntitiesFromAuto(
                request, scenario.uuid, dates)

            if len(entity_ids) == 0:
                message = "no entities found"
                return Response({"success": False, "message": message},
                                status=status.HTTP_404_NOT_FOUND)

            entity_scores = portfolio_count(entity_ids, dates, mode="auto")

            scores = self.getScores(entity_scores, portfolio, entity_ids,
                                    metric="news_count",
                                    func=lambda x: x)
        else:
            return Response({"success": False, "message": "filter not specified"},
                            status=status.HTTP_404_NOT_FOUND)

        return Response({"success": True,
                         "samples": len(scores),
                         "data": scores},
                        status=status.HTTP_200_OK)


class EntityKeywords(views.APIView):
    """
    List keywords under an entity

    # Format
    {
        "entity": "<ENTITY UUID"
    }
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        entity = get_object_or_404(Entity, uuid=request.data["entity"])

        serializer = EntityListSerializer(entity)
        keywords = serializer.data["keywords"]

        if len(keywords) > 0:
            keyword_str = "', '".join(keywords)
            keyword_str = "('{}')".format(keyword_str)

            query = """
                        select search_keyword, count(*) from apis_story
                        where search_keyword in {}
                        group by search_keyword
                    """.format(keyword_str)

            with connection.cursor() as cursor:
                cursor.execute(query)
                columns = [col[0] for col in cursor.description]
                rows = [
                    dict(zip(columns, row))
                    for row in cursor.fetchall()
                ]
                return Response({"success": True,
                                "data": rows},
                                status=status.HTTP_200_OK)
        return Response({"success": False, "message": "No keywords found"},
                        status=status.HTTP_404_NOT_FOUND)
