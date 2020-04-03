from rest_framework import status
from rest_framework import views
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from apis.models.entity import EntityType
from .serializers import EntityTypeSerializer


class ViewEntityType(views.APIView):
    """
    List all Entities and Aliases being Tracked in a Scenario
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # fetch entity objects in portfolio
        entities = EntityType.objects.all()
        serializer = EntityTypeSerializer(entities, many=True)
        return Response({"success": True, "length": len(entities),
                         "data": serializer.data},
                        status=status.HTTP_200_OK)
