from django.db import connection
from datetime import datetime, timedelta


PORTFOLIO_DAYS = 150


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    return [
        {str(row[0]): row[1]}
        for row in cursor.fetchall()
    ]


def get_latest_model_uuid(scenario):
    """
    fetch the latest version of model for the given scenario
    """
    # include scenario here
    query = """
    select uuid from apis_modeldetail am where
    "version"=(select max("version") from apis_modeldetail where "scenarioID_id"='{}')
    """.format(scenario)

    with connection.cursor() as cursor:
        cursor.execute(query)
        row = cursor.fetchone()
    return str(row[0])


def news_count_query(viz_type, uuid, scenario_id=None):
    """
    query to fetch the news count per day of
    * an entity
    * a bucket with grossScore > .2
    """

    if viz_type == "entity":
        query = """
                select published_date::date, count(*) from apis_story as2 
                where "entityID_id" = '{}'
                group by 1 order by 1
                """.format(uuid)
    elif viz_type == "bucket":
        model_id = get_latest_model_uuid(scenario_id)
        query = """
                select published_date::date, count(distinct "storyID_id")
                from apis_entityscore ae
                inner join apis_story sty
                on ae."storyID_id" = sty.uuid
                where ae."bucketID_id"='{}'
                and ae."modelID_id" = '{}'
                and ae."grossScore" > .2
                group by 1 order by 1
                """.format(uuid, model_id)

    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = dictfetchall(cursor)
    return rows


def sentiment_query(viz_type, uuid, sentiment_type, scenario_id=None):
    """
    query to fetch the sentiment per day of
    * an entity
    * a bucket with grossScore > .2
    """

    if viz_type == "entity":
        query = """
                select published_date::date,
                sum(coalesce("sentiment", '0')::float)/count(*) as "sentiment" from
                (select published_date, sentiment->'{}' as "sentiment" from
                apis_story as2
                inner join apis_storysentiment sent
                on as2.uuid=sent."storyID_id"
                where "entityID_id" = '{}') sem
                group by 1 order by 1
                """.format(sentiment_type, uuid)
    elif viz_type == "bucket":
        model_id = get_latest_model_uuid(scenario_id)
        query = """
                select published_date::date,
                sum(coalesce("sentiment", '0')::float)/count(*) as "sentiment" from
                (select published_date, sentiment->'{}' as "sentiment" from
                apis_entityscore ae inner join apis_story sty
                on ae."storyID_id" = sty.uuid
                inner join apis_storysentiment sent
                on sty.uuid=sent."storyID_id"
                where ae."bucketID_id"='{}'
                and ae."modelID_id" = '{}'
                and ae."grossScore" > .2) snt
                group by 1 order by 1
                """.format(sentiment_type, uuid, model_id)

    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = dictfetchall(cursor)
    return rows


def bucket_score_query(viz_type, bucket_id, entity_id=None, scenario_id=None):
    """
    query to fetch the bucket score per day of
    * an entity
    * a bucket with grossScore > .2
    """

    if viz_type == "entity":
        model_id = get_latest_model_uuid(scenario_id)
        query = """
                select published_date::date, sum("grossScore")/count(*)
                as bucket_score from apis_entityscore ae
                inner join apis_story sty on ae."storyID_id" = sty.uuid
                where ae."entityID_id" = '{}'
                and ae."modelID_id" = '{}'
                and ae."bucketID_id"='{}'
                group by 1 order by 1
                """.format(entity_id, model_id, bucket_id)
    elif viz_type == "bucket":
        model_id = get_latest_model_uuid(scenario_id)
        query = """
                select "storyDate"::date, sum("grossScore")/count(*) as bucket_score
                from apis_bucketscore ab
                where ab."modelID_id" = '{}'
                and ab."bucketID_id"='{}'
                group by 1 order by 1
                """.format(model_id, bucket_id)

    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = dictfetchall(cursor)
    return rows
