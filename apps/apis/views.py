import json

from datetime import datetime, timedelta
from django.core import serializers
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from rest_framework.generics import CreateAPIView
from rest_framework import views
from rest_framework import status
from rest_framework import renderers
from rest_framework import parsers
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from .models.scenario import (
    Bucket,
    BucketWeight,
    Scenario
)

from settings.common import EMAIL_HOST_USER

from .models.users import DashUser, Client
from .serializers import (UserSerializer, DashUserSerializer,
                          AuthCustomTokenSerializer, ScenarioSerializer,
                          ClientSerializer, BucketSerializer)


class GenericGET(views.APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

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


class GetUserUUID(views.APIView):
    """
    get uuid by using email and password
    """
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

        dash_user = DashUser.objects.filter(
            **{"user__id": user.id}).first()

        if dash_user:
            content = {
                'user': dash_user.uuid,
            }
            return Response(content,
                            status=status.HTTP_200_OK)
        else:
            msg = "no dash user exists"
            return Response({"message": msg},
                            status=status.HTTP_404_NOT_FOUND)


class SignUp(CreateAPIView):
    """
    Validates the data and creates a new account for a person
    with corresponding Dash User
    """

    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        user_form = UserSerializer(data=request.data)
        dash_user_form = DashUserSerializer(data=request.data)

        if user_form.is_valid(raise_exception=True) and \
           dash_user_form.is_valid(raise_exception=True):
            email = user_form.data['email']

            if User.objects.filter(email=email).exists():
                return Response({"error": "This email id already exists."})

            user_obj = User.objects.create_user(
                first_name=user_form.data['first_name'],
                last_name=user_form.data['last_name'],
                username=user_form.data['email'],
                email=user_form.data['email'],
                password=user_form.data['password'])

            client = get_object_or_404(Client,
                                       uuid=dash_user_form.data['clientID'])
            scenario = get_object_or_404(Scenario,
                                         uuid=dash_user_form.data['defaultScenario'])

            dash_user_obj = DashUser.objects.create(
                user=user_obj,
                status=dash_user_form.data['status'],
                clientID=client,
                defaultScenario=scenario
            )

            # send confirmation email to the new user
            subject = 'Thank you for signing up with Alrt.ai'
            message = 'Welcome to Alrt.ai. Your account has been set up'
            from_email = EMAIL_HOST_USER
            to_list = [email]
            send_mail(subject, message, from_email, to_list, fail_silently=True)

            # create and return a token for the user
            token = Token.objects.create(user=dash_user_obj.user)
            return Response({'token': str(token)}, status=status.HTTP_200_OK)
        return Response({"success": False}, status=status.HTTP_406_NOT_ACCEPTABLE)


class Logout(views.APIView):
    def get(self, request, format=None):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)


class ObtainCustomAuthToken(views.APIView):
    """
    signing in using email and password
    """
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

        return Response(content, status=status.HTTP_200_OK)


class GetClientUUID(GenericGET):
    def post(self, request):
        data = self.getSingleObjectFromPOST(request, "uuid", "uuid", DashUser)
        if data:
            return Response({"success": True, "uuid": data.clientID.uuid},
                            status=status.HTTP_200_OK)
        return Response({"success": False},
                        status=status.HTTP_404_NOT_FOUND)


class GetClientName(GenericGET):
    def post(self, request):
        data = self.getSingleObjectFromPOST(request, "uuid", "uuid", DashUser)
        if data:
            return Response({"success": True, "name": data.clientID.name},
                            status=status.HTTP_200_OK)
        return Response({"success": False},
                        status=status.HTTP_404_NOT_FOUND)


class GetUserStatus(GenericGET):
    def post(self, request):
        data = self.getSingleObjectFromPOST(request, "uuid", "uuid", DashUser)
        if data:
            expired = datetime.date(
                (datetime.now() - timedelta(days=30))) > data.setupDate
            return Response({"success": True,
                             "status": data.status,
                             "date": data.setupDate,
                             "expired": expired
                             },
                            status=status.HTTP_200_OK)
        return Response({"success": False},
                        status=status.HTTP_404_NOT_FOUND)


class GetUserDefaultScenario(GenericGET):
    def post(self, request):
        data = self.getSingleObjectFromPOST(request, "uuid", "uuid", DashUser)
        if data:
            return Response(
                {
                    "success": True,
                    "scenario": data.defaultScenario.name,
                    "scenario_uuid": data.defaultScenario.uuid,
                    "entity_type": data.defaultScenario.entityType.uuid,
                    "mode": data.defaultScenario.mode
                },
                status=status.HTTP_200_OK
            )
        return Response({"success": False},
                        status=status.HTTP_404_NOT_FOUND)


class GetScenarioName(GenericGET):
    def post(self, request):
        data = self.getSingleObjectFromPOST(
            request, "uuid", "uuid", DashUser.defaultScenario.name)
        if data:
            return Response({"success": True, "name": data.name},
                            status=status.HTTP_200_OK)
        return Response({"success": False},
                        status=status.HTTP_404_NOT_FOUND)


class GetBuckets(GenericGET):
    def post(self, request):
        data = self.getManyObjectsFromPOST(
            request, "scenario_uuid", "scenarioID", Bucket)
        if data:
            serializer = BucketSerializer(data, many=True)
            if data:
                return Response(
                    {"success": True, "result": serializer.data},
                    status=status.HTTP_200_OK
                )
        return Response({"success": False},
                        status=status.HTTP_404_NOT_FOUND)


class GetBucketWeights(GenericGET):
    def post(self, request):
        data = self.getManyObjectsFromPOST(
            request, "uuid", "userID", BucketWeight)
        if data:
            return Response(
                {"success": True, "result": serializers.serialize(
                    "json", data)},
                status=status.HTTP_200_OK
            )
        return Response({"success": False},
                        status=status.HTTP_404_NOT_FOUND)


class ListAllScenario(views.APIView):
    def get(self, request, format=None):
        data = Scenario.objects.filter(status="active")
        serializer = ScenarioSerializer(data, many=True)
        if data:
            return Response(
                {"success": True, "result": serializer.data},
                status=status.HTTP_200_OK
            )
        return Response({"success": False},
                        status=status.HTTP_404_NOT_FOUND)


class ListAllClients(views.APIView):
    def get(self, request, format=None):
        data = Client.objects.all()
        serializer = ClientSerializer(data, many=True)
        if data:
            return Response(
                {"success": True, "result": serializer.data},
                status=status.HTTP_200_OK
            )
        return Response({"success": False},
                        status=status.HTTP_404_NOT_FOUND)