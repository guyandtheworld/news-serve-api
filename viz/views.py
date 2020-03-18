from rest_framework import views
from rest_framework.response import Response


class NewsCountViz(views.APIView):
    """
    For a given entity or a bucket, get
    * News Count Per Day
    """
    def post(self, request, format=None):
        return Response({"success": False})


class SentimentViz(views.APIView):
    """
    For a given entity or a bucket, get
    * Normalized Sentiment Per Day (compound/-ve/+ve)
    """
    def post(self, request, format=None):
        return Response({"success": False})


class BucketScoreViz(views.APIView):
    """
    For a given entity or a bucket, get
    * Normalized Bucket Score Per Day (all buckets)

    From a bucket viz for the past year, we can
    see if there is a spike in financial crime
    for a given entity
    """
    def post(self, request, format=None):
        return Response({"success": False})
