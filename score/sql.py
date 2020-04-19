from django.db import connection


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
    and "scenarioID_id"='{}'
    """.format(scenario, scenario)

    with connection.cursor() as cursor:
        cursor.execute(query)
        row = cursor.fetchone()
    if row:
        return "'{}'".format(str(row[0]))
    else:
        return False


def portfolio_score(entity_ids, scenario_id, dates):
    """
    Returns GrossScore, bucket and timedelta from published date for
    aggregate GrossScore creation where bucket is other
    """

    entity_ids = "', '".join(entity_ids)
    entity_ids = "('{}')".format(entity_ids)
    start_date = "'{}'".format(dates[0])
    end_date = "'{}'".format(dates[1])
    model_id = get_latest_model_uuid(scenario_id)

    if not model_id:
        return ()

    query = """
            select entity_score."entityID_id"::text, entity."name",
            "bucketID_id"::text, "grossScore", entity_type."name" as "type",
            extract(year from age(CURRENT_TIMESTAMP, published_date)) * 12 +
            extract(month from age(CURRENT_TIMESTAMP, published_date)) as "timeDiff" from
            apis_entityscore entity_score inner join apis_story story on entity_score."storyID_id" = story.uuid
            inner join apis_bucket bucket on entity_score."bucketID_id" = bucket.uuid
            inner join apis_storyentityref entity on entity_score."entityID_id" = entity.uuid
            inner join apis_entitytype entity_type on entity."typeID_id" = entity_type.uuid
            where entity_score."entityID_id" in {} and model_label != 'other'
            and "modelID_id" = {} and published_date > %s and published_date <= %s
            """.format(entity_ids, model_id)

    with connection.cursor() as cursor:
        cursor.execute(query, [start_date, end_date])
        rows = dictfetchall(cursor)
    return rows


def bucket_score(bucket_ids, scenario_id, dates):
    """
    Returns GrossScore for each Bucket, bucket and timedelta
    from published date for aggregate GrossScore creation
    where bucket is not other
    """
    start_date = "'{}'".format(dates[0])
    end_date = "'{}'".format(dates[1])
    bucket_ids = "', '".join(bucket_ids)
    bucket_ids = "('{}')".format(bucket_ids)

    model_id = get_latest_model_uuid(scenario_id)

    if not model_id:
        return ()

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
            and published_date > %s and published_date <= %s
            """.format(bucket_ids, model_id)

    with connection.cursor() as cursor:
        cursor.execute(query, [start_date, end_date])
        rows = dictfetchall(cursor)
    return rows


def entity_bucket_score(entity_id, scenario_id, dates):
    """
    Returns GrossScore, bucket and timedelta for
    a given entity
    """
    start_date = "'{}'".format(dates[0])
    end_date = "'{}'".format(dates[1])
    model_id = get_latest_model_uuid(scenario_id)

    if not model_id:
        return ()

    query = """
            select bckt."name", "bucketID_id"::text, "grossScore",
            extract(year from age(CURRENT_TIMESTAMP, published_date)) * 12 +
            extract(month from age(CURRENT_TIMESTAMP, published_date)) as "timeDiff" from
            apis_entityscore ae
            inner join apis_story sty
            on ae."storyID_id" = sty.uuid
            inner join apis_bucket bckt
            on ae."bucketID_id" = bckt.uuid
            where ae."entityID_id" = %s
            and "modelID_id" = {}
            and model_label != 'other'
            and published_date > %s and published_date <= %s
            """.format(model_id)

    with connection.cursor() as cursor:
        cursor.execute(query, [entity_id, start_date, end_date])
        rows = dictfetchall(cursor)
    return rows


def portfolio_count(entity_ids, dates, mode):
    """
    Returns news count for a user's portfolio
    """

    entity_ids = "', '".join(entity_ids)
    entity_ids = "('{}')".format(entity_ids)
    start_date = "'{}'".format(dates[0])
    end_date = "'{}'".format(dates[1])

    if mode == "portfolio":
        query = """
                select entty.name, entty.uuid, news_count from
                (select "entityID_id", count(*) as news_count from
                apis_story as2 where published_date > %s and published_date <= %s
                group by "entityID_id") grby
                inner join apis_entity entty on grby."entityID_id" = entty.uuid
                where entty.uuid in {}
                """.format(entity_ids)
    else:
        query = """
                select entty.name, entty.uuid, news_count from
                (select "entityID_id", count(*) as news_count
                from apis_storyentitymap as2
                inner join
                (select uuid, published_date from apis_story where
                published_date > %s and published_date <= %s) story
                on as2."storyID_id" = story.uuid
                group by "entityID_id") grby
                inner join apis_storyentityref entty on grby."entityID_id" = entty.uuid
                where entty.uuid in {}
                """.format(entity_ids)

    with connection.cursor() as cursor:
        cursor.execute(query, [start_date, end_date])
        rows = dictfetchall(cursor)
    return rows


def portfolio_sentiment(entity_ids, dates, mode):
    """
    Returns news count for a user's portfolio
    """
    start_date = "'{}'".format(dates[0])
    end_date = "'{}'".format(dates[1])
    entity_ids = "', '".join(entity_ids)
    entity_ids = "('{}')".format(entity_ids)

    if mode == "portfolio":
        query = """
                select entty."name", "entityID_id", sentiment->'compound' as "sentiment",
                extract(year from age(CURRENT_TIMESTAMP, published_date)) * 12 +
                extract(month from age(CURRENT_TIMESTAMP, published_date)) as "timeDiff" from
                apis_storysentiment as2
                inner join apis_story sty
                on as2."storyID_id" = sty.uuid
                inner join apis_storyentityref entty
                on "entityID_id" = entty.uuid
                where entty.uuid in {}
                and published_date > %s and published_date <= %s
                """.format(entity_ids)
    else:
        query = """
                select as3."name", as2."entityID_id", sentiment->'compound' as "sentiment",
                extract(year from age(CURRENT_TIMESTAMP, published_date)) * 12 +
                extract(month from age(CURRENT_TIMESTAMP, published_date)) as "timeDiff" from
                apis_storyentitymap as2
                inner join apis_story sty
                on as2."storyID_id" = sty.uuid
                inner join apis_storyentityref as3
                on as2."entityID_id" = as3.uuid
                inner join apis_storysentiment stysent
                on stysent."storyID_id" = sty.uuid
                where as2."entityID_id" in {}
                and published_date > %s and published_date <= %s
                """.format(entity_ids)

    with connection.cursor() as cursor:
        cursor.execute(query, [start_date, end_date])
        rows = dictfetchall(cursor)
    return rows
