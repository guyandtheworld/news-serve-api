from django.shortcuts import render
from rest_framework import views
from rest_framework.response import Response


class Test(views.APIView):
    def get(self, request):
        return Response("TEST")
