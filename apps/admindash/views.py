from django.shortcuts import get_object_or_404

from rest_framework import views
from rest_framework import status
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAdminUser

from apis.models.entity import Entity, Alias
from apis.models.scenario import Scenario

from .serializers import (VerifiableEntitySerializer, EntityUpdateSerializer,
                          AliasUpdateSerializer, UnverifiedScenarioSerializer)


class ListVerifiableEntities(views.APIView):
    """
    List all entities and aliases that are not verfied by the user

    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]

    def get(self, request):

        entities = Entity.objects.filter(entryVerified=False)

        if len(entities) > 0:
            # fetch entitities that are not verified
            serializer = VerifiableEntitySerializer(entities, many=True)

            return Response({"success": True, "length": len(entities),
                             "data": serializer.data}, status=status.HTTP_200_OK)
        msg = "all entities are verified"
        return Response({"success": False, "data": msg}, status=status.HTTP_404_NOT_FOUND)


class UpdateEntities(views.APIView):

    # To make changes to an existing entity from the table
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]

    def delete(self, request):
        """
        To delete an entity from the table

        # Format

        {
            "entity": "<ENTITY UUID>"
        }
        """
        entity = get_object_or_404(Entity, request.data["entity"])
        entity.delete()
        msg = "entity deleted"
        return Response({"success": True, "data": msg},
                        status=status.HTTP_200_OK
                        )

    def put(self, request):
        """
        To update an entity with new values

        # format
        {
        "entity": "<ENTITY UUID>",
        "name": " ",
        "lei": "",
        "dbpediaResource": " ",
        "wikiResource": " ",
        "manualEntry": true,
        "entityType": " ",
        "scenarioID": " "
        }
        """

        entity = get_object_or_404(Entity, uuid=request.data["entity"])

        serializer = EntityUpdateSerializer(entity, data=request.data,
                                            partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "data": serializer.data},
                            status=status.HTTP_200_OK
                            )


class UpdateAlias(views.APIView):
    # Make changes to alias added by the user after verification

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]

    def delete(self, request):
        """
        Delete alias added by the user after verification

        # Format

        {
            "alias": "<ALIAS UUID>"
        }
        """

        alias = get_object_or_404(Alias, request.data["alias"])
        alias.delete()
        msg = "alias deleted"
        return Response({"success": True, "data": msg},
                        status=status.HTTP_200_OK
                        )

    def put(self, request):
        """
        Update alias added by the user after verification

        # Format

        {
            "alias": "<ALIAS UUID>",
            "name": "<NEW ALIAS NAME>"
        }
        """

        alias = get_object_or_404(Alias, uuid=request.data["alias"])

        serializer = AliasUpdateSerializer(alias, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "data": serializer.data},
                            status=status.HTTP_200_OK
                            )


class VerifyEntity(views.APIView):
    """
    Set entry verified as true for the entity

    # Format

    {
        "entity": "<ENTITY UUID>"
    }
    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]

    def put(self, request):

        entity = get_object_or_404(Entity, uuid=request.data["entity"])
        data = {"entryVerified": True}
        serializer = EntityUpdateSerializer(entity, data=data,
                                            partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True,
                             "entryVerified": serializer.data["entryVerified"]},
                            status=status.HTTP_200_OK
                            )


class UnverifiedScenarios(views.APIView):
    """
    List all scenarios created by the user and not verfied

    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]

    def get(self, request):

        scenarios = Scenario.objects.filter(status="unverified")

        if len(scenarios) > 0:
            # fetch scenarios that are not verified
            serializer = UnverifiedScenarioSerializer(scenarios, many=True)
            return Response({"success": True, "length": len(scenarios),
                             "data": serializer.data}, status=status.HTTP_200_OK)
        msg = "all scenarios are verified"
        return Response({"success": False, "data": msg}, status=status.HTTP_404_NOT_FOUND)
