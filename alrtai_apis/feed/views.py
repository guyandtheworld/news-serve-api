import json
from django.shortcuts import render
from django.core import serializers
from rest_framework import views
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from apis.models.users import User, Portfolio
from apis.models.scenario import Scenario


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
            if obj == None:
                return False
            return obj
        return False

    def getManyObjectsFromPOST(self, request, key, column, ModelName):
        if key in request.data:
            data = request.data[key]
            obj = ModelName.objects.filter(**{column: data})
            if obj == None:
                return False
            return obj
        return False


class GetPortfolio(GenericGET):
    def post(self, request):
        user = self.getSingleObjectFromPOST(request, "uuid", "uuid", User)
        scenario = self.getSingleObjectFromPOST(request, "scenario", "name", Scenario)
        if user and scenario:
            portfolio = Portfolio.objects.filter(**{"userID": user.uuid, "scenarioID": scenario.uuid})
            print(portfolio)
            return Response({"success": True, "uuid": user.uuid})
        return Response({"success": False})


# DAYS = 150


# @blueprint.route("/portfolio", methods=["GET"])
# def feed():
#     """
#     generate feed of news for all companies in portfolio
#     """

#     # get all companies in the user's portfolio
#     try:
#         companies = EntityIndex.objects.filter(actively_tracking=True)
#     except Exception as e:
#         print(e)
#         return {"status": "failed to fetch companies from mongodb"}, 500

#     if len(companies) == 0:
#         return {"status": "no companies found"}, 200

#     companies_id = [company.id for company in companies]

#     # fetch all the articles of the required companies
#     # which are from the past 6 month and that's active
#     start_date = datetime.now() - timedelta(days=DAYS)

#     try:
#         pipeline = [{"$match": {"entity_id": {"$in": companies_id}}},
#                     {"$match": {"status_code": 200}},
#                     {"$match": {"language": "english"}},
#                     {"$match": {"published_date": {"$gt": start_date}}},
#                     {"$lookup":
#                      {
#                          "from": EntityIndex._get_collection_name(),
#                          "localField": "entity_id",
#                          "foreignField": "_id",
#                          "as": "company"
#                      }},
#                     {
#                         "$unwind": "$company"},
#                     {
#                     "$project": {
#                         "_id": 1,
#                         "title": 1,
#                         "url": 1,
#                         "body": 1,
#                         "unique_hash": 1,
#                         "search_keyword": 1,
#                         "published_date": 1,
#                         "domain": 1,
#                         "language": 1,
#                         "source_country": 1,
#                         "title_analytics": 1,
#                         "body_analytics": 1,
#                         "company.entity_id": 1,
#                         "company.entity_legal_name": 1, }
#                     }]
#         articles = Article.objects.aggregate(*pipeline)
#     except Exception as e:
#         print(e)
#         return {"status": "failed to fetch articles from mongodb"}, 500

#     articles = list(articles)
#     if len(articles) == 0:
#         return {"status": "no articles found"}, 200

#     json_data = score_in_bulk(articles)

#     return {"status": "success", "samples": len(json_data),
#             "data": json_data}, 200


# @blueprint.route("/company/id=<int:entity_id>", methods=["GET"])
# def company_feed(entity_id):
#     """
#     generate feed of news for all companies in portfolio
#     """

#     # get all companies in the user's portfolio
#     try:
#         company = EntityIndex.objects.get(entity_id=entity_id)
#     except Exception as e:
#         print(e)
#         return {"status": "failed to fetch companies from mongodb"}, 500

#     if len(company) == 0:
#         return {"status": "no companies found"}, 200

#     # fetch all the articles of the required companies
#     # which are from the past 6 month and that's active
#     start_date = datetime.now() - timedelta(days=DAYS)

#     try:
#         pipeline = [{"$match": {"entity_id": company.id}},
#                     # {"$match": {"status_code": 200}},
#                     {"$match": {"language": "english"}},
#                     {"$match": {"published_date": {"$gt": start_date}}},
#                     {"$project": {
#                         "_id": 1,
#                         "title": 1,
#                         "url": 1,
#                         "body": 1,
#                         "unique_hash": 1,
#                         "search_keyword": 1,
#                         "published_date": 1,
#                         "domain": 1,
#                         "language": 1,
#                         "source_country": 1,
#                         "title_analytics": 1,
#                         "body_analytics": 1}
#                      }]
#         articles = Article.objects.aggregate(*pipeline)
#     except Exception as e:
#         print(e)
#         return {"status": "failed to fetch articles from mongodb"}, 500

#     articles = list(articles)

#     if len(articles) == 0:
#         return {"status": "no articles found"}, 200

#     json_data = score_in_bulk(articles)

#     return {"status": "success", "samples": len(json_data),
#             "data": json_data}, 200


# @blueprint.route("/company/sentiment/id=<int:entity_id>", methods=["GET"])
# def company_sentiment(entity_id):
#     """
#     generate sentiment score for the company for a year
#     * how to normalize?
#     * sample the data with an upper limit
#     """

#     # get all companies in the user's portfolio
#     try:
#         company = EntityIndex.objects.get(entity_id=entity_id)
#     except Exception as e:
#         print(e)
#         return {"status": "failed to fetch companies from mongodb"}, 500

#     if len(company) == 0:
#         return {"status": "no companies found"}, 200

#     # fetch all the articles of the required companies
#     # which are from the past 6 month and that's active
#     start_date = datetime.now() - timedelta(days=365)

#     try:
#         pipeline = [{"$match": {"entity_id": company.id}},
#                     {"$match": {"language": "english"}},
#                     {"$match": {"published_date": {"$gt": start_date}}},
#                     {"$project": {
#                         "_id": 0,
#                         "published_date": 1,
#                         "title_analytics.vader_sentiment_score": 1}
#                      }]

#         sentiment = Article.objects.aggregate(*pipeline)
#     except Exception as e:
#         print(e)
#         return {"status": "failed to fetch articles from mongodb"}, 500

#     sentiment = pd.DataFrame(list(sentiment))

#     if len(sentiment) == 0:
#         return {"status": "no articles found"}, 200

#     print(sentiment.head())
#     return {"status": "success", "samples": len(sentiment),
#             "data": sentiment.to_dict(orient='records')}, 200


# @blueprint.route("/company/metrics/id=<int:entity_id>", methods=["GET"])
# def company_metrics(entity_id):
#     """
#     generate metrics for the company
#     * language
#     * country
#     * domain
#     * news count
#     * negative/positive news count
#     * most common bucket
#     """

#     # get all companies in the user's portfolio
#     try:
#         company = EntityIndex.objects.get(entity_id=entity_id)
#     except Exception as e:
#         print(e)
#         return {"status": "failed to fetch companies from mongodb"}, 500

#     if len(company) == 0:
#         return {"status": "no companies found"}, 200

#     return {"status": "success"}, 200
