import json
from django.shortcuts import render
from django.http import JsonResponse
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


class GetUserUUID(views.APIView):
    def get(self, request):
        return Response("Send POST request with JSON object with email as a key")

    def post(self, request):
        if "email" in request.data:
            email = request.data["email"]
            user_uuid = User.objects.filter(email=email).first()
            if user_uuid == None:
                return Response({"success": False})
            return Response({"success": True, "uuid": user_uuid.uuid})
        return Response("Invalid object in request")


class GetClientUUID(views.APIView):
    def get(self, request):
        return Response("Send POST request with JSON object with uuid as a key")

    def post(self, request):
        if "uuid" in request.data:
            uuid = request.data["uuid"]
            user = User.objects.filter(uuid=uuid).first()
            if user == None:
                return Response({"success": False})
            return Response({"success": True, "uuid": user.clientID.uuid})
        return Response("Invalid object in request")
