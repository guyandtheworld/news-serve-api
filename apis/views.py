import json

from django.core import serializers
from rest_framework.generics import CreateAPIView
from rest_framework import views
from rest_framework import status
from rest_framework import renderers
from rest_framework import parsers
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from .models.scenario import (
    Bucket,
    BucketWeight,
)

from .models.users import DashUser
from .serializers import EntitySerializer, AliasSerializer, UserSerializer, DashUserSerializer, AuthCustomTokenSerializer


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
            if obj is None:
                return False
            return obj
        return False

    def getManyObjectsFromPOST(self, request, key, column, ModelName):
        if key in request.data:
            data = request.data[key]
            obj = ModelName.objects.filter(**{column: data})
            if obj is None:
                return False
            return obj
        return False


class GetUserUUID(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super(GetUserUUID, self).post(
            request, *args, **kwargs)
        token = Token.objects.get(key=response.data['token'])
        dash_user = DashUser.objects.filter(
            **{"user__id": token.user_id}).first()
        return Response({'uuid': dash_user.uuid})


class GetClientUUID(GenericGET):
    def post(self, request):
        data = self.getSingleObjectFromPOST(request, "uuid", "uuid", DashUser)
        if data:
            return Response({"success": True, "uuid": data.clientID.uuid})
        return Response({"success": False})


class GetClientName(GenericGET):
    def post(self, request):
        data = self.getSingleObjectFromPOST(request, "uuid", "uuid", DashUser)
        if data:
            return Response({"success": True, "name": data.clientID.name})
        return Response({"success": False})


class GetUserStatus(GenericGET):
    def post(self, request):
        data = self.getSingleObjectFromPOST(request, "uuid", "uuid", DashUser)
        if data:
            return Response({"success": True, "status": data.status})
        return Response({"success": False})


class GetUserDefaultScenario(GenericGET):
    def post(self, request):
        data = self.getSingleObjectFromPOST(request, "uuid", "uuid", DashUser)
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
        data = self.getSingleObjectFromPOST(
            request, "uuid", "uuid", DashUser.defaultScenario.name)
        if data:
            return Response({"success": True, "name": data.name})
        return Response({"success": False})


class GetBuckets(GenericGET):
    def post(self, request):
        data = self.getManyObjectsFromPOST(
            request, "uuid", "scenarioID", Bucket)
        if data:
            return Response(
                {"success": True, "result": serializers.serialize(
                    "json", data)}
            )
        return Response({"success": False})


class GetBucketWeights(GenericGET):
    def post(self, request):
        data = self.getManyObjectsFromPOST(
            request, "uuid", "userID", BucketWeight)
        if data:
            return Response(
                {"success": True, "result": serializers.serialize(
                    "json", data)}
            )
        return Response({"success": False})


class AddEntity(CreateAPIView):
    """
    End-point to create entity.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        entity_serializer = EntitySerializer(data=request.data)
        if entity_serializer.is_valid():
            entity = entity_serializer.save()
            return Response(
                {"success": True, "entity_uuid": entity.uuid}
            )


class AddAlias(CreateAPIView):
    """
    End-point to create alias.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        alias_serializer = AliasSerializer(data=request.data, many=True)
        if alias_serializer.is_valid():
            alias = alias_serializer.save()
            alias_uuid = []
            for obj in alias:
                alias_uuid.append(obj.uuid)
            return Response(
                {"success": True, "alias_uuid": alias_uuid}
            )


class Logout(views.APIView):
    def get(self, request, format=None):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)


class SignUp(CreateAPIView):
    def post(self, request, *args, **kwargs):
        user_form = UserSerializer(data=request.data)
        dash_user_form = DashUserSerializer(data=request.data)

        if user_form.is_valid(raise_exception=True) and \
           dash_user_form.is_valid(raise_exception=True):

            user_obj = user_form.save()
            dash_user_obj = dash_user_form.save()
            dash_user_obj.user = user_obj
            dash_user_obj.save()
            token = Token.objects.create(user=user_obj)
            return Response({'token': str(token)})
        return Response({"success": False})


class ObtainCustomAuthToken(views.APIView):
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (
        parsers.FormParser,
        parsers.MultiPartParser,
        parsers.JSONParser,
    )

    renderer_classes = (renderers.JSONRenderer,)

    def post(self, request):
        serializer = AuthCustomTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)

        content = {
            'token': str(token.key),
        }

        return Response(content)
