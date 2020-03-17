from rest_framework import views
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated


from apis.models.users import Portfolio
from .utils import get_anchors, get_alias


class AddEntityInfo(views.APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        entity = request.data["entity"]
        if entity:
            data = get_anchors(entity)
            return Response({"success": True, "data": data})
        return Response({"success": False})


class AddEntityAlias(views.APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        entity = request.data["entity"]
        if entity:
            data = get_alias(entity)
            return Response({"success": True, "data": data})
        return Response({"success": False})


class ListPortfolio(views.APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.data["user"]
        portfolio = Portfolio.objects.filter(userID=user)
        print(portfolio)
        if user:
            return Response({"success": True, "data": portfolio[0].uuid})
        return Response({"success": False})
