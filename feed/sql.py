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
            published_date, internal_source, "domain",
            entry_created, "language", source_country,
            raw_file_source, "entityID_id", stry_bdy_tbl.body,
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
        """.format(ids_str)

    with connection.cursor() as cursor:
        cursor.execute(query, [start_date])
        rows = dictfetchall(cursor)
    return rows
