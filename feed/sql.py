from django.db import connection
from datetime import datetime, timedelta


PORTFOLIO_DAYS = 150

# get entity name, and story body
# get entities from title and body
# get sentiment from title and body
EXTRA_INFO = """
            inner join
            apis_entity ent
            on stry."entityID_id" = ent.uuid
            inner join
            (select "storyID_id", body from
            apis_storybody) stry_bdy_tbl
            on stry_bdy_tbl."storyID_id" = stry.uuid
            inner join
            (select "storyID_id", entities
            from apis_storyentities
            where is_headline = true) title_entities
            on title_entities."storyID_id" = stry.uuid
            inner join
            (select "storyID_id", sentiment
            from apis_storysentiment
            where is_headline = true) title_sntmnt
            on title_sntmnt."storyID_id" = stry.uuid
            left join
            (select "storyID_id", entities
            from apis_storyentities
            where is_headline = false) body_entities
            on body_entities."storyID_id" = stry.uuid
            left join
            (select "storyID_id", sentiment
            from apis_storysentiment
            where is_headline = false) body_sentiment
            on body_sentiment."storyID_id" = stry.uuid
            """

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def user_portfolio(entity_ids):
    """
    query to filter stories based on the portfolio
    language and published date and then return
    the body, entities, and sentiment of the
    title as well as the body
    """

    ids_str = "', '".join(entity_ids)
    ids_str = "('{}')".format(ids_str)
    start_date = datetime.now() - timedelta(days=PORTFOLIO_DAYS)
    start_date = "'{}'".format(start_date)

    query = """
            select distinct unique_hash, stry.uuid,
            title, stry.url, search_keyword,
            published_date, "domain", source_country,
            "entityID_id", ent."name", stry_bdy_tbl.body,
            title_entities.entities as title_entities,
            title_sntmnt.sentiment as title_sentiment,
            body_entities.entities as body_entities,
            body_sentiment.sentiment as body_sentiment
            FROM public.apis_story as stry
            inner join
            (select * from apis_storybody as2
            where status_code = 200) as stby
            on stry.uuid = stby."storyID_id"
            and "language" in ('english', 'US', 'CA', 'AU', 'IE')
            and "entityID_id" in {}
            and published_date > %s
            {}
        """.format(ids_str, EXTRA_INFO)

    with connection.cursor() as cursor:
        cursor.execute(query, [start_date])
        rows = dictfetchall(cursor)
    return rows


def user_entity(entity_id):
    """
    query to filter stories based on the entity
    language and published date and then return
    the body, entities, and sentiment of the
    title as well as the body
    """

    id_str = "'{}'".format(entity_id)
    start_date = datetime.now() - timedelta(days=PORTFOLIO_DAYS)
    start_date = "'{}'".format(start_date)

    query = """
            select distinct unique_hash, stry.uuid,
            title, stry.url, search_keyword,
            published_date, "domain", source_country,
            "entityID_id", ent."name", stry_bdy_tbl.body,
            title_entities.entities as title_entities,
            title_sntmnt.sentiment as title_sentiment,
            body_entities.entities as body_entities,
            body_sentiment.sentiment as body_sentiment
            FROM public.apis_story as stry
            inner join
            (select * from apis_storybody as2
            where status_code = 200) as stby
            on stry.uuid = stby."storyID_id"
            and "language" in ('english', 'US', 'CA', 'AU', 'IE')
            and "entityID_id" = {}
            and published_date > %s
            {}
        """.format(id_str, EXTRA_INFO)

    with connection.cursor() as cursor:
        cursor.execute(query, [start_date])
        rows = dictfetchall(cursor)
    return rows


def user_bucket(bucket_id):
    """
    given a bucket id, generate feed to score the articles
    """
    start_date = datetime.now() - timedelta(days=PORTFOLIO_DAYS)
    start_date = "'{}'".format(start_date)

    query = """
            select distinct unique_hash, stry.uuid,
            title, stry.url, search_keyword,
            published_date, internal_source, "domain",
            source_country, "entityID_id", ent."name", "language",
            "storyDate", "source", "grossScore", "sourceScore",
            title_entities.entities as title_entities,
            title_sntmnt.sentiment as title_sentiment,
            body_entities.entities as body_entities,
            body_sentiment.sentiment as body_sentiment,
            stry_bdy_tbl.body from apis_story stry
            inner join
            (select "storyID_id", "storyDate", src."name" as source,
            "grossScore", src.score as "sourceScore" from
            (select * from apis_bucketscore where
            "bucketID_id" = '2fa858cf-f8c3-4fe8-bd02-ae66aae2b909') bktscr
            inner join (select * from apis_source) src
            on src.uuid = bktscr."sourceID_id") tbl
            on stry.uuid = tbl."storyID_id"
            and "language" in ('english', 'US', 'CA', 'AU', 'IE')
            and published_date > %s
            {}
            """.format(EXTRA_INFO)

    with connection.cursor() as cursor:
        cursor.execute(query, [start_date])
        rows = dictfetchall(cursor)
    return rows
