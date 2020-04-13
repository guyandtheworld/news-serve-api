from django.db import connection


PORTFOLIO_DAYS = 150

# get entity name, and story body
# get entities from title and body
# get sentiment from title and body
EXTRA_INFO_PORT = """
            inner join apis_entity ent on stry."entityID_id" = ent.uuid
            inner join (select "storyID_id", body from apis_storybody) stry_bdy_tbl
            on stry_bdy_tbl."storyID_id" = stry.uuid
            inner join
            (select "storyID_id", sentiment from apis_storysentiment where is_headline = true) title_sntmnt
            on title_sntmnt."storyID_id" = stry.uuid
            left join
            (select "storyID_id", sentiment from apis_storysentiment where is_headline = false) body_sentiment
            on body_sentiment."storyID_id" = stry.uuid
            """

EXTRA_INFO_AUTO = """
            inner join apis_storyentityref ent on entitymap."entityID_id" = ent.uuid
            inner join (select "storyID_id", body from apis_storybody) stry_bdy_tbl
            on stry_bdy_tbl."storyID_id" = stry.uuid
            inner join
            (select "storyID_id", sentiment from apis_storysentiment where is_headline = true) title_sntmnt
            on title_sntmnt."storyID_id" = stry.uuid
            left join
            (select "storyID_id", sentiment from apis_storysentiment where is_headline = false) body_sentiment
            on body_sentiment."storyID_id" = stry.uuid
            """


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
    return str(row[0])

def user_portfolio(entity_ids, dates, mode):
    """
    query to filter stories based on the portfolio
    language and published date and then return
    the body, entities, and sentiment of the
    title as well as the body
    """

    ids_str = "', '".join(entity_ids)
    ids_str = "('{}')".format(ids_str)
    start_date = "'{}'".format(dates[0])
    end_date = "'{}'".format(dates[1])

    if mode == 'portfolio':
        query = """
                select distinct unique_hash, stry.uuid, title, stry.url, search_keyword,
                published_date, "domain", source_country, "entityID_id", ent."name", stry_bdy_tbl.body,
                title_sntmnt.sentiment as title_sentiment,body_sentiment.sentiment as body_sentiment
                FROM public.apis_story as stry
                inner join
                (select * from apis_storybody as2 where status_code = 200) as stby
                on stry.uuid = stby."storyID_id" and "language" in ('english', 'US', 'CA', 'AU', 'IE')
                and "entityID_id" in {}
                and published_date > %s and published_date <= %s {}
            """.format(ids_str, EXTRA_INFO_PORT)
    elif mode == "auto":
        query = """
                select distinct unique_hash, stry.uuid, title, stry.url, search_keyword,
                published_date, "domain", source_country, entitymap."entityID_id", ent."name", stry_bdy_tbl.body,
                title_sntmnt.sentiment as title_sentiment,body_sentiment.sentiment as body_sentiment
                from apis_storyentitymap entitymap
                inner join apis_story stry
                on entitymap."storyID_id" = stry.uuid
                inner join
                (select * from apis_storybody as2 where status_code = 200) as stby
                on stry.uuid = stby."storyID_id" and "language" in ('english', 'US', 'CA', 'AU', 'IE')
                and entitymap."entityID_id" in {}
                and published_date > %s and published_date <= %s {}
                """.format(ids_str, EXTRA_INFO_AUTO)

    with connection.cursor() as cursor:
        cursor.execute(query, [start_date, end_date])
        rows = dictfetchall(cursor)
    return rows

def user_entity(entity_id, dates, mode):
    """
    query to filter stories based on the entity
    language and published date and then return
    the body, entities, and sentiment of the
    title as well as the body
    """

    id_str = "'{}'".format(entity_id)
    start_date = "'{}'".format(dates[0])
    end_date = "'{}'".format(dates[1])
    if mode == 'portfolio':
        query = """
                select distinct unique_hash, stry.uuid, title, stry.url, search_keyword,
                published_date, "domain", source_country, "entityID_id", ent."name", stry_bdy_tbl.body,
                title_sntmnt.sentiment as title_sentiment,body_sentiment.sentiment as body_sentiment
                FROM public.apis_story as stry
                inner join
                (select * from apis_storybody as2 where status_code = 200) as stby
                on stry.uuid = stby."storyID_id" and "language" in ('english', 'US', 'CA', 'AU', 'IE')
                and "entityID_id" = {}
                and published_date > %s and published_date <= %s {}
                """.format(id_str, EXTRA_INFO_PORT)
    elif mode == "auto":
        query = """
                select distinct unique_hash, stry.uuid, title, stry.url, search_keyword,
                published_date, "domain", source_country, entitymap."entityID_id", ent."name", stry_bdy_tbl.body,
                title_sntmnt.sentiment as title_sentiment, body_sentiment.sentiment as body_sentiment
                from apis_storyentitymap entitymap
                inner join apis_story stry
                on entitymap."storyID_id" = stry.uuid
                inner join
                (select * from apis_storybody as2 where status_code = 200) as stby
                on stry.uuid = stby."storyID_id" and "language" in ('english', 'US', 'CA', 'AU', 'IE')
                and entitymap."entityID_id" = {}
                and published_date > %s and published_date <= %s {}
                """.format(id_str, EXTRA_INFO_AUTO)
    with connection.cursor() as cursor:
        cursor.execute(query, [start_date, end_date])
        rows = dictfetchall(cursor)
    return rows


def user_bucket(bucket_id, entity_ids, scenario_id, dates, mode):

    """
    given a bucket id, generate feed to score the articles
    """
    start_date = "'{}'".format(dates[0])
    end_date = "'{}'".format(dates[1])
    bucket_id = "'{}'".format(bucket_id)

    ids_str = "', '".join(entity_ids)
    entity_ids = "('{}')".format(ids_str)
    
    model_id = get_latest_model_uuid(scenario_id)

    if mode == 'portfolio':
        query = """
                select distinct unique_hash, stry.uuid, title, stry.url, search_keyword,
                published_date, internal_source, "domain", source_country, "entityID_id", ent."name", "language",
                "source", "grossScore", "sourceScore",title_sntmnt.sentiment as title_sentiment,
                body_sentiment.sentiment as body_sentiment, stry_bdy_tbl.body from apis_story stry
                inner join
                (select "storyID_id", "storyDate", src."name" as source, "grossScore", src.score as "sourceScore" from
                (select * from apis_bucketscore where "bucketID_id" = {} and "modelID_id"='{}' and "grossScore" > .7) bktscr
                inner join
                (select * from apis_source) src
                on src.uuid = bktscr."sourceID_id") tbl
                on stry.uuid = tbl."storyID_id"
                and "language" in ('english', 'US', 'CA', 'AU', 'IE')
                and published_date > %s and published_date <= %s
                and "entityID_id" in {}
                {}
                """.format(bucket_id, model_id, entity_ids, EXTRA_INFO_PORT)
    elif mode == "auto":
        query = """
                select distinct unique_hash, stry.uuid, title, stry.url, search_keyword,
                published_date, internal_source, "domain", source_country, entitymap."entityID_id", ent."name", "language",
                "source", "grossScore", "sourceScore", title_sntmnt.sentiment as title_sentiment,
                body_sentiment.sentiment as body_sentiment, stry_bdy_tbl.body
                from apis_storyentitymap entitymap
                inner join apis_story stry
                on entitymap."storyID_id" = stry.uuid
                inner join
                (select "storyID_id", "storyDate", src."name" as source, "grossScore", src.score as "sourceScore" from
                (select * from apis_bucketscore where "bucketID_id" = {} and "modelID_id"='{}' and "grossScore" > .7) bktscr
                inner join
                (select * from apis_source) src
                on src.uuid = bktscr."sourceID_id") tbl
                on stry.uuid = tbl."storyID_id"
                and "language" in ('english', 'US', 'CA', 'AU', 'IE')
                and published_date > %s and published_date <= %s
                and "entityID_id" in {}
                {}
                """.format(bucket_id, model_id, entity_ids, EXTRA_INFO_AUTO)
    with connection.cursor() as cursor:
        cursor.execute(query, [start_date, end_date])
        rows = dictfetchall(cursor)
    return rows



def user_entity_bucket(bucket_id, entity_id, scenario_id, dates, mode):
    """
    get all articles for a particular entity if it falls under
    a bucket
    """
    bucket_id = "'{}'".format(bucket_id)
    entity_id = "'{}'".format(entity_id)
    start_date = "'{}'".format(dates[0])
    end_date = "'{}'".format(dates[1])

    # get latest model version uuid
    model_id = get_latest_model_uuid(scenario_id)

    if mode == 'portfolio':
        query = """
                select distinct unique_hash, stry.uuid, title, stry.url, search_keyword,
                published_date, internal_source, "domain", source_country, "entityID_id", ent."name", "language",
                "source", "grossScore", "sourceScore", title_sntmnt.sentiment as title_sentiment,
                body_sentiment.sentiment as body_sentiment, stry_bdy_tbl.body from apis_story stry
                inner join
                (select "storyID_id", "storyDate", src."name" as source, "grossScore", src.score as "sourceScore" from
                (select * from apis_bucketscore where "bucketID_id" = {} and "modelID_id"='{}' and "grossScore" > .7) bktscr
                inner join
                (select * from apis_source) src
                on src.uuid = bktscr."sourceID_id") tbl
                on stry.uuid = tbl."storyID_id"
                and "language" in ('english', 'US', 'CA', 'AU', 'IE')
                and published_date > %s and published_date <= %s
                and "entityID_id" = {}
                {}
                """.format(bucket_id, model_id, entity_id, EXTRA_INFO_PORT)
    elif mode == "auto":
        query = """
                select distinct unique_hash, stry.uuid, title, stry.url, search_keyword,
                published_date, internal_source, "domain", source_country, entitymap."entityID_id", ent."name", "language",
                "source", "grossScore", "sourceScore", title_sntmnt.sentiment as title_sentiment,
                body_sentiment.sentiment as body_sentiment, stry_bdy_tbl.body
                from apis_storyentitymap entitymap
                inner join apis_story stry
                on entitymap."storyID_id" = stry.uuid
                inner join
                (select "storyID_id", "storyDate", src."name" as source, "grossScore", src.score as "sourceScore" from
                (select * from apis_bucketscore where "bucketID_id" = {} and "modelID_id"='{}' and "grossScore" > .7) bktscr
                inner join
                (select * from apis_source) src
                on src.uuid = bktscr."sourceID_id") tbl
                on stry.uuid = tbl."storyID_id"
                and "language" in ('english', 'US', 'CA', 'AU', 'IE')
                and published_date > %s and published_date <= %s
                and "entityID_id" = {}
                {}
                """.format(bucket_id, model_id, entity_id, EXTRA_INFO_AUTO)

    with connection.cursor() as cursor:
        cursor.execute(query, [start_date, end_date])
        rows = dictfetchall(cursor)
    return rows


def story_entities(story_ids):
    """
    takes a list of story ids and queries the apis_storyentitymap to find
    the list of entities in thsoe stories
    """

    ids_str = "', '".join(story_ids)
    story_ids = "('{}')".format(ids_str)

    query = """
        select sem.uuid,"storyID_id",name,type,"entityID_id" from apis_storyentitymap as sem
        inner join apis_storyentityref as enref on sem."entityID_id" = enref.uuid
        inner join (select name as type,uuid as type_id from apis_entitytype) as entype on enref."typeID_id" = entype.type_id
        where "storyID_id" in {}
        """.format(story_ids)

    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = dictfetchall(cursor)
    return rows
