from datetime import datetime
from django.shortcuts import get_object_or_404
from django.db import connection

from rest_framework import status
from rest_framework import views
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from apis.models.users import DashUser
from apis.models.story import EntityScore
from apis.models.entity import (EntityType,
                                StoryEntityRef,
                                StoryEntityMap)
from entity.models import Alias
from .serializers import (EntityTypeSerializer,
                          AliasListSerializer,
                          ParentNameSerializer,
                          StoryEntityMapSerializer,
                          EntityScoreSerializer,
                          AliasChangeSerializer)


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


class ListParentAlias(views.APIView):
    """
    List all the aliases of a parent entity

    # Format

        {
            "uuid": "<PARENT UUID>"
        }
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):

        parent = get_object_or_404(StoryEntityRef, uuid=request.data["uuid"])
        alias = Alias.objects.filter(parentID=parent)

        if len(alias) > 0:
            serializer = AliasListSerializer(alias, many=True)

            return Response({"success": True, "length": len(alias),
                             "data": serializer.data},
                            status=status.HTTP_200_OK)

        return Response({"success": False},
                        status=status.HTTP_404_NOT_FOUND)


class ChangeParentName(views.APIView):
    """
    Change parent name with an alias

    # Format

        {
            "uuid": "<PARENT UUID>",
            "name": "<ALIAS NAME>"
        }
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request):

        parent = get_object_or_404(StoryEntityRef, uuid=request.data["uuid"])
        serializer = ParentNameSerializer(parent, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "result": serializer.data},
                            status=status.HTTP_200_OK
                            )


class MergeParents(views.APIView):
    """
    merge two similar parents into a single entity

    # Format

    * "user": dashuser.uuid,
    * "parent": storyentityref.uuid,
    * "children": list(storyentityref.uuid)
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):

        parent = get_object_or_404(StoryEntityRef, uuid=request.data["parent"])
        user = get_object_or_404(DashUser, uuid=request.data["user"])

        cursor = connection.cursor()

        children = []
        for child in request.data["children"]:
            obj = get_object_or_404(StoryEntityRef, uuid=child)
            children.append(obj)

        # Change entityID of stories to the preserving parent
        for child in children:
            query = """UPDATE public.apis_storyentitymap
                       SET "entityID_id"='{}', updated_at='{}',
                       updated_by_id='{}', last_value='{}'
                       WHERE "entityID_id"='{}';""".format(str(parent.uuid),
                                                           str(datetime.now()),
                                                           str(user.uuid),
                                                           child.name,
                                                           str(child.uuid))
            cursor.execute(query)

        # Change the entityID of entityScore to the preserving parent
        for child in children:
            query = """UPDATE public.apis_entityscore
                       SET "entityID_id"='{}', updated_at='{}',
                       updated_by_id='{}', last_value='{}'
                       WHERE "entityID_id"='{}';""".format(str(parent.uuid),
                                                           str(datetime.now()),
                                                           str(user.uuid),
                                                           child.name,
                                                           str(child.uuid))
            cursor.execute(query)

        # Change the parentID of aliases to the preserving parent
        for child in children:
            query = """UPDATE public.entity_alias
                       SET "parentID_id"='{}', updated_at='{}',
                       updated_by_id='{}', last_value='{}'
                       WHERE "parentID_id"='{}';""".format(str(parent.uuid),
                                                           str(datetime.now()),
                                                           str(user.uuid),
                                                           child.name,
                                                           str(child.uuid))
            cursor.execute(query)

        # # Delete the merging parent from StoryEntityref
        for child in children:
            child.delete()

        return Response({"success": True},
                        status=status.HTTP_200_OK
                        )
