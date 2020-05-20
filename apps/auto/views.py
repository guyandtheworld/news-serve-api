from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework import views
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

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

        if len(alias)>0:
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

        {
            "uuid1": "<PRESERVING PARENT UUID>",
            "uuid2": "<MERGING PARENT UUID>"
        }
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):

        parent = get_object_or_404(StoryEntityRef, uuid=request.data["uuid1"])
        merging_parent =  get_object_or_404(StoryEntityRef, uuid=request.data["uuid2"])

        # Change entityID of stories to the preserving parent
        stories_parent = StoryEntityMap.objects.filter(entityID=parent)
        story_ids = []
        for parent_story in stories_parent:
            story_ids.append(parent_story.storyID)

        stories = StoryEntityMap.objects.filter(entityID=merging_parent)
        if len(stories)>0:
            data = {"entityID":parent.uuid}
            for story in stories:
                if story.storyID not in story_ids:
                    serializer = StoryEntityMapSerializer(story, data=data)
                    if serializer.is_valid():
                        serializer.save()
                    else:
                        return Response({"success": False},
                                        status=status.HTTP_404_NOT_FOUND
                                        )

        # Change the entityID of entityScore to the preserving parent
        entity_scores = EntityScore.objects.filter(entityID=merging_parent)
        if len(entity_scores)>0:
            data = {"entityID":parent.uuid}
            for score in entity_scores:
                serializer = EntityScoreSerializer(score, data=data)
                if serializer.is_valid():
                    serializer.save()
                else:
                    return Response({"success": False},
                                    status=status.HTTP_404_NOT_FOUND
                                    )

        # Change the parentID of aliases to the preserving parent
        aliases = Alias.objects.filter(parentID=merging_parent)
        if len(aliases)>0:
            data = {"parentID":parent.uuid}
            for alias in aliases:
                serializer = AliasChangeSerializer(alias, data=data)
                if serializer.is_valid():
                    serializer.save()
                else:
                    return Response({"success": False},
                                    status=status.HTTP_404_NOT_FOUND
                                    )
        
        # Delete the merging parent from StoryEntityref
        merging_parent.delete()
        return Response({"success": True},
                                status=status.HTTP_200_OK
                                )
