from django.db import connection
from datetime import datetime, timedelta


PORTFOLIO_DAYS = 150

start_date = datetime.now() - timedelta(days=PORTFOLIO_DAYS)
START_DATE = "'{}'".format(start_date)


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
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
    return "'{}'".format(str(row[0]))


def portfolio_score(entity_ids, scenario_id):
    """
    Returns GrossScore, bucket and timedelta from published date for
    aggregate GrossScore creation where bucket is other
    """

    entity_ids = "', '".join(entity_ids)
    entity_ids = "('{}')".format(entity_ids)

    model_id = get_latest_model_uuid(scenario_id)

    query = """
            select ae."entityID_id"::text, entty."name", "bucketID_id"::text, "grossScore",
            extract(year from age(CURRENT_TIMESTAMP, published_date)) * 12 +
            extract(month from age(CURRENT_TIMESTAMP, published_date)) as "timeDiff" from
            apis_entityscore ae
            inner join apis_story sty
            on ae."storyID_id" = sty.uuid
            inner join apis_bucket bckt
            on ae."bucketID_id" = bckt.uuid
            inner join apis_entity entty
            on ae."entityID_id" = entty.uuid
            where ae."entityID_id" in {}
            and model_label != 'other'
            and "modelID_id" = {}
            and published_date > %s
            """.format(entity_ids, model_id)

    with connection.cursor() as cursor:
        cursor.execute(query, [START_DATE])
        rows = dictfetchall(cursor)
    return rows


def bucket_score(bucket_ids, scenario_id):
    """
    Returns GrossScore for each Bucket, bucket and timedelta
    from published date for aggregate GrossScore creation
    where bucket is not other
    """

    bucket_ids = "', '".join(bucket_ids)
    bucket_ids = "('{}')".format(bucket_ids)

    model_id = get_latest_model_uuid(scenario_id)

    query = """
            select bckt."name", "bucketID_id"::text, "grossScore",
            extract(year from age(CURRENT_TIMESTAMP, published_date)) * 12 +
            extract(month from age(CURRENT_TIMESTAMP, published_date)) as "timeDiff" from
            apis_bucketscore ae
            inner join apis_story sty
            on ae."storyID_id" = sty.uuid
            inner join apis_bucket bckt
            on ae."bucketID_id" = bckt.uuid
            where "bucketID_id" in {}
            and "modelID_id" = {}
            and published_date > %s
            """.format(bucket_ids, model_id)

    with connection.cursor() as cursor:
        cursor.execute(query, [START_DATE])
        rows = dictfetchall(cursor)
    return rows


def entity_bucket_score(entity_id, scenario_id):
    """
    Returns GrossScore, bucket and timedelta for
    a given entity
    """

    model_id = get_latest_model_uuid(scenario_id)

    query = """
            select bckt."name", "bucketID_id"::text, "grossScore",
            extract(year from age(CURRENT_TIMESTAMP, published_date)) * 12 +
            extract(month from age(CURRENT_TIMESTAMP, published_date)) as "timeDiff" from
            apis_entityscore ae
            inner join apis_story sty
            on ae."storyID_id" = sty.uuid
            inner join apis_bucket bckt
            on ae."bucketID_id" = bckt.uuid
            inner join apis_entity entty
            on ae."entityID_id" = entty.uuid
            where ae."entityID_id" = %s
            and "modelID_id" = {}
            and model_label != 'other'
            and published_date > %s
            """.format(model_id)

    with connection.cursor() as cursor:
        cursor.execute(query, [entity_id, START_DATE])
        rows = dictfetchall(cursor)
    return rows


def portfolio_count(entity_ids):
    """
    Returns news count for a user's portfolio
    """

    entity_ids = "', '".join(entity_ids)
    entity_ids = "('{}')".format(entity_ids)

    query = """
            select entty.name, entty.uuid, news_count from
            (select "entityID_id", count(*) as news_count from
            apis_story as2 group by "entityID_id") grby
            inner join apis_entity entty on grby."entityID_id" = entty.uuid
            where entty.uuid in {}
            """.format(entity_ids)

    with connection.cursor() as cursor:
        cursor.execute(query, [START_DATE])
        rows = dictfetchall(cursor)
    return rows


def portfolio_sentiment(entity_ids):
    """
    Returns news count for a user's portfolio
    """

    entity_ids = "', '".join(entity_ids)
    entity_ids = "('{}')".format(entity_ids)

    query = """
            select entty."name", "entityID_id", sentiment->'compound' as "sentiment",
            extract(year from age(CURRENT_TIMESTAMP, published_date)) * 12 +
            extract(month from age(CURRENT_TIMESTAMP, published_date)) as "timeDiff" from
            apis_storysentiment as2
            inner join apis_story sty
            on as2."storyID_id" = sty.uuid
            inner join apis_entity entty
            on "entityID_id" = entty.uuid
            where entty.uuid in {}
            and published_date > %s
            """.format(entity_ids)

    with connection.cursor() as cursor:
        cursor.execute(query, [START_DATE])
        rows = dictfetchall(cursor)
    return rows