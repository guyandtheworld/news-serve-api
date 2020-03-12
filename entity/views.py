from rest_framework import views
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from .utils import get_anchors, get_alias


class GetEntityInfo(views.APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        entity = request.data["entity"]
        if entity:
            data = get_anchors(entity)
            return Response({"success": True, "data": data})


class GetEntityAlias(views.APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        entity = request.data["entity"]
        if entity:
            print(entity)
            data = get_alias(entity)
            return Response({"success": True, "data": data})
