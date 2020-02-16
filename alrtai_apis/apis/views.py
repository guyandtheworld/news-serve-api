import json
from django.shortcuts import render
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
        return Response("Send POST request with JSON object with email as a key")

    def getSingleObjectFromPOST(self, request, key, column):
        if key in request.data:
            data = request.data[key]
            obj = User.objects.filter(**{column: data}).first()
            if obj == None:
                return False
            return obj
        return False


class GetUserUUID(GenericGET):
    def post(self, request):
        data = self.getSingleObjectFromPOST(request, "email", "email")
        if data:
            return Response({"success": True, "uuid": data.uuid})
        return Response({"success": False})


class GetClientUUID(GenericGET):
    def post(self, request):
        data = self.getSingleObjectFromPOST(request, "uuid", "uuid")
        if data:
            return Response({"success": True, "uuid": data.clientID.uuid})
        return Response({"success": False})
