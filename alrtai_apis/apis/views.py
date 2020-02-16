import json
from django.shortcuts import render
from django.core import serializers
from rest_framework import views
from rest_framework.response import Response
from .models.scenario import (
    Scenario,
    Bucket,
    BucketWeight,
    ModelDetails,
    BucketModel,
    Source,
)
from .models.users import User, Client, UserScenario


class Test(views.APIView):
    def get(self, request):
        return Response("TEST")


class GenericGET(views.APIView):
    def get(self, request):
        return Response("Send POST request with JSON object with the correct key")

    def getSingleObjectFromPOST(self, request, key, column, ModelName):
        if key in request.data:
            data = request.data[key]
            obj = ModelName.objects.filter(**{column: data}).first()
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
        data = self.getSingleObjectFromPOST(request, "uuid", "uuid", Client)
        if data:
            return Response({"success": True, "name": data.name})
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
        data = self.getSingleObjectFromPOST(request, "uuid", "uuid", Scenario)
        if data:
            return Response({"success": True, "status": data.name})
        return Response({"success": False})
