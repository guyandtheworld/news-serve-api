from django.db import connection


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    return [
        {str(row[0]): row[1]} for row in cursor.fetchall()]


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
    return str(row[0])


def news_count_query(viz_type, uuid, dates, scenario_id=None, mode=None):
    """
    query to fetch the news count per day of
    * an entity
    * a bucket with grossScore > .2
    """
    start_date = "'{}'".format(dates[0])
    end_date = "'{}'".format(dates[1])
    if viz_type == "entity":
        if mode == "portfolio":
            query = """
                    select published_date::date, count(*) from apis_story as2
                    where "entityID_id" = '{}'
                    and published_date > %s and published_date <= %s
                    group by 1 order by 1
                    """.format(uuid)
        else:
            query = """
                    select published_date::date, count(distinct url) from apis_storyentitymap as3
                    left join apis_story sty
                    on sty.uuid = as3."storyID_id"
                    where as3."entityID_id" = '{}'
                    and published_date > %s and published_date <= %s
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
                and published_date > %s and published_date <= %s
                group by 1 order by 1
                """.format(uuid, model_id)

    with connection.cursor() as cursor:
        cursor.execute(query, [start_date, end_date])
        rows = dictfetchall(cursor)
    return rows


def sentiment_query(viz_type, uuid, sentiment_type, dates, scenario_id=None, mode=None):
    """
    query to fetch the sentiment per day of
    * an entity
    * a bucket with grossScore > .2
    """
    start_date = "'{}'".format(dates[0])
    end_date = "'{}'".format(dates[1])
    if viz_type == "entity":
        if mode == "portfolio":
            query = """
                    select published_date::date,
                    sum(coalesce("sentiment", '0')::float)/count(*) as "sentiment" from
                    (select published_date, sentiment->'{}' as "sentiment" from
                    apis_story as2
                    inner join apis_storysentiment sent
                    on as2.uuid=sent."storyID_id"
                    where "entityID_id" = '{}') sem
                    where published_date > %s and published_date <= %s
                    group by 1 order by 1
                    """.format(sentiment_type, uuid)
        else:
            query = """
                    select published_date::date,
                    sum(coalesce("sentiment", '0')::float)/count(*) as "sentiment" from
                    (select published_date, sentiment->'{}' as "sentiment" from
                    apis_storyentitymap as3
                    inner join
                    apis_story sty
                    on sty.uuid = as3."storyID_id"
                    inner join apis_storysentiment sent
                    on sty.uuid=sent."storyID_id"
                    where as3."entityID_id" = '{}') sem
                    where published_date > %s and published_date <= %s
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
                where published_date > %s and published_date <= %s
                group by 1 order by 1
                """.format(sentiment_type, uuid, model_id)

    with connection.cursor() as cursor:
        cursor.execute(query, [start_date, end_date])
        rows = dictfetchall(cursor)
    return rows


def bucket_score_query(viz_type, bucket_id, dates, entity_id=None, scenario_id=None):
    """
    query to fetch the bucket score per day of
    * an entity
    * a bucket with grossScore > .2
    """
    start_date = "'{}'".format(dates[0])
    end_date = "'{}'".format(dates[1])
    if viz_type == "entity":
        model_id = get_latest_model_uuid(scenario_id)
        query = """
                select published_date::date, sum("grossScore")/count(*)
                as bucket_score from apis_entityscore ae
                inner join apis_story sty on ae."storyID_id" = sty.uuid
                where ae."entityID_id" = '{}'
                and ae."modelID_id" = '{}'
                and ae."bucketID_id"='{}'
                and published_date > %s and published_date <= %s
                group by 1 order by 1
                """.format(entity_id, model_id, bucket_id)
    elif viz_type == "bucket":
        model_id = get_latest_model_uuid(scenario_id)
        query = """
                select "storyDate"::date, sum("grossScore")/count(*) as bucket_score
                from apis_bucketscore ab
                inner join apis_story sty on ab."storyID_id" = sty.uuid
                where ab."modelID_id" = '{}'
                and ab."bucketID_id"='{}'
                and published_date > %s and published_date <= %s
                group by 1 order by 1
                """.format(model_id, bucket_id)

    with connection.cursor() as cursor:
        cursor.execute(query, [start_date, end_date])
        rows = dictfetchall(cursor)
    return rows


def get_entity_stories(dates, entity_id, mode):
    dates_str = "', '".join(dates)
    dates_str = "('{}')".format(dates_str)

    if mode == "portfolio":
        query = """
                select published_date::date, (array_agg(json_build_array(url, title)))[0:10] article from
                (select distinct url, title, published_date from apis_story stry
                where published_date::date in {}
                and "entityID_id" = '{}') tbl
                group by 1 order by 1
                """.format(dates_str, entity_id)
    elif mode == "auto":
        query = """
                select published_date::date, (array_agg(json_build_array(url, title)))[0:10] article from
                (select distinct url, title, published_date from apis_storyentitymap mp
                left join apis_story stry on mp."storyID_id"=stry.uuid
                where published_date::date in {}
                and mp."entityID_id" = '{}') tbl
                group by 1 order by 1
                """.format(dates_str, entity_id)

    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = dictfetchall(cursor)
    return rows

def get_count_per_country(dates):
    start_date = "'{}'".format(dates[0])
    end_date = "'{}'".format(dates[1])

    query = """select source_country,count(title) from apis_story
    where published_date > %s and published_date <= %s
    group by source_country
    """
    with connection.cursor() as cursor:
        cursor.execute(query, [start_date, end_date])
        rows = cursor.fetchall()
    return rows
