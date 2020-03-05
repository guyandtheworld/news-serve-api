from django.db import connection
from datetime import datetime, timedelta


PORTFOLIO_DAYS = 15

start_date = datetime.now() - timedelta(days=PORTFOLIO_DAYS)
START_DATE = "'{}'".format(start_date)


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def portfolio_score(entity_ids):
    """
    Returns GrossScore, bucket and timedelta from published date for
    aggregate GrossScore creation where bucket is other
    """

    entity_ids = "', '".join(entity_ids)
    entity_ids = "('{}')".format(entity_ids)

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
            and published_date > %s
            """.format(entity_ids)

    with connection.cursor() as cursor:
        cursor.execute(query, [START_DATE])
        rows = dictfetchall(cursor)
    return rows


def bucket_score(bucket_ids):
    """
    Returns GrossScore for each Bucket, bucket and timedelta
    from published date for aggregate GrossScore creation
    where bucket is not other
    """

    bucket_ids = "', '".join(bucket_ids)
    bucket_ids = "('{}')".format(bucket_ids)

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
            and published_date > %s
            """.format(bucket_ids)

    with connection.cursor() as cursor:
        cursor.execute(query, [START_DATE])
        rows = dictfetchall(cursor)
    return rows
