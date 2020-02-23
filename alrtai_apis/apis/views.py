import json
from django.shortcuts import render
from django.core import serializers
from rest_framework.generics import CreateAPIView
from rest_framework import views
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .models.scenario import (
    Scenario,
    Bucket,
    BucketWeight,
    ModelDetail,
    BucketModel,
    Source,
)
from .models.users import User, Client, UserScenario
from .models.entity import Entity
from .seralizers import EntitySerializer, AliasSerializer

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
            if obj == None:
                return False
            return obj
        return False

    def getManyObjectsFromPOST(self, request, key, column, ModelName):
        if key in request.data:
            data = request.data[key]
            obj = ModelName.objects.filter(**{column: data})
            if obj == None:
                return False
            return obj
        return False


class GetUserUUID(GenericGET):
    def post(self, request):
        data = self.getSingleObjectFromPOST(request, "email", "email", User)
        if data:
            return Response({"success": True, "uuid": data.uuid})
        return Response({"success": False})


class GetClientUUID(GenericGET):
    def post(self, request):
        data = self.getSingleObjectFromPOST(request, "uuid", "uuid", User)
        if data:
            return Response({"success": True, "uuid": data.clientID.uuid})
        return Response({"success": False})


class GetClientName(GenericGET):
    def post(self, request):
        data = self.getSingleObjectFromPOST(request, "uuid", "uuid", User)
        if data:
            return Response({"success": True, "name": data.clientID.name})
        return Response({"success": False})


class GetUserStatus(GenericGET):
    def post(self, request):
        data = self.getSingleObjectFromPOST(request, "uuid", "uuid", User)
        if data:
            return Response({"success": True, "status": data.status})
        return Response({"success": False})


class GetUserDefaultScenario(GenericGET):
    def post(self, request):
        data = self.getSingleObjectFromPOST(request, "uuid", "uuid", User)
        if data:
            return Response(
                {
                    "success": True,
                    "result": serializers.serialize("json", [data.defaultScenario]),
                }
            )
        return Response({"success": False})


class GetScenarioName(GenericGET):
    def post(self, request):
        data = self.getSingleObjectFromPOST(request, "uuid", "uuid", User.defaultScenario.name)
        if data:
            return Response({"success": True, "name": data.name})
        return Response({"success": False})


class GetBuckets(GenericGET):
    def post(self, request):
        data = self.getManyObjectsFromPOST(request, "uuid", "scenarioID", Bucket)
        if data:
            return Response(
                {"success": True, "result": serializers.serialize("json", data)}
            )
        return Response({"success": False})


class GetBucketWeights(GenericGET):
    def post(self, request):
        data = self.getManyObjectsFromPOST(request, "uuid", "userID", BucketWeight)
        if data:
            return Response(
                {"success": True, "result": serializers.serialize("json", data)}
            )
        return Response({"success": False})

class AddEntity(CreateAPIView):
    serializer_class = EntitySerializer

class AddAlias(CreateAPIView):
    serializer_class = AliasSerializer