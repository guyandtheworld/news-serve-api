from django.shortcuts import get_object_or_404

from rest_framework import views
from rest_framework import status
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAdminUser

from apis.models.entity import Entity
from apis.models.scenario import Scenario, Bucket

from .serializers import (EntitySerializer,
                          ScenarioSerializer,
                          BucketSerializer)


class ListVerifiableEntities(views.APIView):
    """
    List all entities that are not verfied by the user

    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]

    def get(self, request):

        entities = Entity.objects.filter(entryVerified=False)

        if len(entities) > 0:
            # fetch entitities that are not verified
            serializer = EntitySerializer(entities, many=True)

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
        "keywords": [""]
        }
        """

        entity = get_object_or_404(Entity, uuid=request.data["entity"])

        serializer = EntitySerializer(entity, data=request.data,
                                            partial=True)
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
        serializer = EntitySerializer(entity, data=data,
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
            serializer = ScenarioSerializer(scenarios, many=True)
            return Response({"success": True, "length": len(scenarios),
                             "data": serializer.data}, status=status.HTTP_200_OK)
        msg = "all scenarios are verified"
        return Response({"success": False, "data": msg}, status=status.HTTP_404_NOT_FOUND)


class AdminScenarioList(views.APIView):
    """
    List all scenarios in the database

    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]

    def get(self, request, format=None):
        data = Scenario.objects.all()
        serializer = ScenarioSerializer(data, many=True)
        if data:
            return Response(
                {"success": True, "result": serializer.data},
                status=status.HTTP_200_OK
            )
        return Response({"success": False},
                        status=status.HTTP_404_NOT_FOUND)


class UpdateBucket(views.APIView):

    # To make changes to an existing entity from the table
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]

    def put(self, request):
        """
        To update a bucket with new values

        # format
        {
        "bucket": "<bucket UUID>",
        "name": " ",
        "description": " ",
        "keywords": [""]
        }
        """
        bucket = get_object_or_404(Bucket, uuid=request.data["bucket"])

        serializer = BucketSerializer(bucket, data=request.data,
                                            partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "data": serializer.data},
                            status=status.HTTP_200_OK
                            )
    
    def delete(self, request):
        """
        To delete a bucket from the table

        # Format

        {
            "bucket": "<BUCKET UUID>"
        }
        """
        bucket = get_object_or_404(Bucket, uuid=request.data["bucket"])
        bucket.delete()
        msg = "Bucket is deleted"
        return Response({"success": True, "data": msg},
                        status=status.HTTP_200_OK
                        )
