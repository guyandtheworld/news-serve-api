from django.db import connection
from datetime import datetime, timedelta


PORTFOLIO_DAYS = 150


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
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
