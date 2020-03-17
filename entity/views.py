from django.shortcuts import get_object_or_404

from rest_framework import views
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from apis.models.users import DashUser, Portfolio
from apis.models.entity import Entity, Alias
from .utils import get_anchors, get_alias
from .serializers import EntitySerializer


class AddEntityInfo(views.APIView):
    """
    Add anchor information to a Particular Entity
    * Wikipedia
    * Dbpedia
    * LEI
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        entity = request.data["entity"]
        if entity:
            data = get_anchors(entity)
            return Response({"success": True, "data": data})
        return Response({"success": False})


class AddEntityAlias(views.APIView):
    """
    Auto-fetch Alias for an Entity from Dbpedia
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        entity = request.data["entity"]
        if entity:
            data = get_alias(entity)
            return Response({"success": True, "data": data})
        return Response({"success": False})


class ListPortfolio(views.APIView):
    """
    List all Entities and Alias in the Portfolio of a Particular User
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = get_object_or_404(DashUser, uuid=request.data["user"])
        portfolio = Portfolio.objects.filter(userID=user)
        if len(portfolio) > 0:
            # fetch entity objects in portfolio
            entities = [en.entityID for en in portfolio]
            serializer = EntitySerializer(entities, many=True)
            return Response({"success": True, "data": serializer.data})
        msg = "no entities in the portfolio"
        return Response({"success": False, "data": msg})


class ListAllEntitiesInScenario(views.APIView):
    """
    List all Entities and Aliases being Tracked in a Scenario
    """
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    # def post(self, request):
    #     entity_serializer = EntitySerializer(data=request.data, many=True))
    #     if entity_serializer.is_valid():
    #         entity = entity_serializer.save()
    #         return Response(
    #             {"success": True, "entity_uuid": entity.uuid}
    #         )
    pass


class AddToPortfolio(views.APIView):
    """
    Add an Entity to the Portfolio of a User
    """
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    # def post(self, request):
    #     entity_serializer = EntitySerializer(data=request.data, many=True))
    #     if entity_serializer.is_valid():
    #         entity = entity_serializer.save()
    #         return Response(
    #             {"success": True, "entity_uuid": entity.uuid}
    #         )
    pass


class CreateEntity(views.APIView):
    """
    Create Entity with Alias for a Particular Scenario
    and adds it to the Portfolio of the User
    """
    pass
