from django.db import connection
from datetime import datetime, timedelta


PORTFOLIO_DAYS = 150


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def portfolio_score(entity_ids):
    """
    Returns GrossScore and timedelta from published date for
    aggregate GrossScore creation
    """
    # id_str = "'{}'".format(entity_id)

    query = """
            select "grossScore",
            extract(year from age(CURRENT_TIMESTAMP, published_date)) * 12 +
            extract(month from age(CURRENT_TIMESTAMP, published_date)) as "timeDiff"
            from apis_entityscore ae inner join apis_story sty
            on ae."storyID_id" = sty.uuid
            where ae."entityID_id"='7970dac1-ca3c-4dc0-814f-f13226eb14db'
            and "bucketID_id"='2fa858cf-f8c3-4fe8-bd02-ae66aae2b909'
            and published_date > '2020-01-01'
            """

    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = dictfetchall(cursor)
    return rows

