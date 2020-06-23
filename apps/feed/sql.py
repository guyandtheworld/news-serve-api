from django.db import connection


COUNT = 20


def dictfetchall(query, start_date=None, end_date=None):
    """
    Return all rows from a cursor as a dict
    """
    with connection.cursor() as cursor:
        if start_date is not None and end_date is not None:
            cursor.execute(query, [start_date, end_date])
        else:
            cursor.execute(query)
        columns = [col[0] for col in cursor.description]
        rows = [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]
    return rows


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


def user_portfolio(entity_ids, scenario_id, dates, mode, page):
    """
    Query to generate feed based on the multiple entities.
    """

    entity_ids_str = "', '".join(entity_ids)
    entity_ids_str = "('{}')".format(entity_ids_str)
    start_date = "'{}'".format(dates[0])
    end_date = "'{}'".format(dates[1])
    decay = dates[2]

    # used for pagination
    limit = COUNT * page
    offset = limit - COUNT

    if mode == "portfolio":
        query = """
                SELECT distinct title, feed."storyID", feed.url, published_date,
                "domain", source_country, entity_name, "entityID",
                "scenarioID", LEFT(story_body, 400), "cluster", entities,
                feed.hotness->'general' AS hotness
                from feed_portfoliowarehouse feed inner join
                (select distinct url, uuid, "storyID",
                CASE WHEN days = 0 THEN hotness::float
                WHEN "decay" = FALSE THEN hotness::float
                ELSE hotness::float * EXP(-0.01 * days * days)
                END AS hotness
                from (select uuid, "storyID", url, hotness->'general' as hotness,
                current_date - published_date::date as days, {} as "decay"
                from feed_portfoliowarehouse
                where published_date > %s and published_date <= %s
                and "entityID" in {}) temphot) hottable
                on feed.uuid = hottable.uuid
                ORDER BY hotness desc OFFSET {} LIMIT {}
                """.format(decay, entity_ids_str, offset, limit)
    elif mode == "auto":
        query = """
                SELECT distinct title, "storyID", url, published_date,
                "domain", source_country, entity_name, "entityID",
                "scenarioID", body, "cluster", entities,
                CASE WHEN days = 0 THEN hotness::float
                WHEN "decay" = FALSE THEN hotness::float
                ELSE hotness::float * EXP(-0.01 * days * days)
                END AS hotness from
                (SELECT distinct url, title, "storyID", published_date,
                "domain", source_country, entity_name, "entityID",
                "scenarioID", LEFT(story_body, 400) as body, "cluster", entities,
                hotness->'general' as hotness,
                current_date - published_date::date as days, {} as "decay"
                FROM feed_autowarehouse
                WHERE published_date > %s AND published_date <= %s
                AND "scenarioID" = '{}' AND "entityID" in {}) hottable
                ORDER BY hotness desc OFFSET {} LIMIT {}
                """.format(decay, scenario_id, entity_ids_str, offset, limit)
    rows = dictfetchall(query, start_date, end_date)
    return rows


def user_entity(entity_id, scenario_id, dates, mode, page, search_keyword=None):
    """
    Query to generate feed based on the entity.
    """

    entity_id_str = "'{}'".format(entity_id)
    keyword = "'{}'".format(search_keyword)
    start_date = "'{}'".format(dates[0])
    end_date = "'{}'".format(dates[1])
    decay = dates[2]

    # used for pagination
    limit = COUNT * page
    offset = limit - COUNT

    if mode == "keyword":
        query = """
                SELECT distinct title, feed."storyID", feed.url, published_date,
                "domain", source_country, entity_name, "entityID",
                "scenarioID", LEFT(story_body, 400), "cluster", entities,
                feed.hotness->'general' AS hotness
                from feed_portfoliowarehouse feed inner join
                (select distinct url, uuid, "storyID",
                CASE WHEN days = 0 THEN hotness::float
                WHEN "decay" = FALSE THEN hotness::float
                ELSE hotness::float * EXP(-0.01 * days * days)
                END AS hotness
                from (select uuid, "storyID", url, hotness->'general' as hotness,
                current_date - published_date::date as days, {} as "decay"
                from feed_portfoliowarehouse
                where published_date > %s and published_date <= %s
                and "search_keyword" = {}) temphot) hottable
                on feed.uuid = hottable.uuid
                ORDER BY hotness desc OFFSET {} LIMIT {}
                """.format(decay, keyword, offset, limit)
    elif mode == "portfolio":
        query = """
                SELECT distinct title, feed."storyID", feed.url, published_date,
                "domain", source_country, entity_name, "entityID",
                "scenarioID", LEFT(story_body, 400), "cluster", entities,
                feed.hotness->'general' AS hotness
                from feed_portfoliowarehouse feed inner join
                (select distinct url, uuid, "storyID",
                CASE WHEN days = 0 THEN hotness::float
                WHEN "decay" = FALSE THEN hotness::float
                ELSE hotness::float * EXP(-0.01 * days * days)
                END AS hotness
                from (select uuid, "storyID", url, hotness->'general' as hotness,
                current_date - published_date::date as days, {} as "decay"
                from feed_portfoliowarehouse
                where published_date > %s and published_date <= %s
                and "entityID" = {}) temphot) hottable
                on feed.uuid = hottable.uuid
                ORDER BY hotness desc OFFSET {} LIMIT {}
                """.format(decay, entity_id_str, offset, limit)
    elif mode == "auto":
        query = """
                SELECT distinct title, "storyID", url, published_date,
                "domain", source_country, entity_name, "entityID",
                "scenarioID", body, "cluster", entities,
                CASE WHEN days = 0 THEN hotness::float
                WHEN "decay" = FALSE THEN hotness::float
                ELSE hotness::float * EXP(-0.01 * days * days)
                END AS hotness from
                (SELECT distinct url, title, "storyID", published_date,
                "domain", source_country, entity_name, "entityID",
                "scenarioID", LEFT(story_body, 400) as body, "cluster", entities,
                hotness->'general' as hotness,
                current_date - published_date::date as days, {} as "decay"
                FROM feed_autowarehouse
                WHERE published_date > %s AND published_date <= %s
                AND "scenarioID" = '{}' AND "entityID" = {}) hottable
                ORDER BY hotness desc OFFSET {} LIMIT {}
                """.format(decay, scenario_id, entity_id_str, offset, limit)

    rows = dictfetchall(query, start_date, end_date)
    return rows


def user_bucket(bucket_id, entity_ids, scenario_id, dates, mode, page):
    """
    Query to generate feed based on the bucket for multiple entities.
    """

    entity_ids_str = "', '".join(entity_ids)
    entity_ids_str = "('{}')".format(entity_ids_str)
    start_date = "'{}'".format(dates[0])
    end_date = "'{}'".format(dates[1])
    decay = dates[2]

    # used for pagination
    limit = COUNT * page
    offset = limit - COUNT

    if mode == "portfolio":
        query = """
                SELECT distinct title, feed."storyID", feed.url, published_date,
                "domain", source_country, entity_name, "entityID",
                "scenarioID", LEFT(story_body, 400), "cluster", entities,
                feed.hotness->'general' AS hotness
                from feed_portfoliowarehouse feed inner join
                (select distinct url, uuid, "storyID",
                CASE WHEN days = 0 THEN hotness::float
                WHEN "decay" = FALSE THEN hotness::float
                ELSE hotness::float * EXP(-0.01 * days * days)
                END AS hotness
                from (select uuid, "storyID", url, hotness->'{}' as hotness,
                current_date - published_date::date as days, {} as "decay"
                from feed_portfoliowarehouse
                where published_date > %s and published_date <= %s
                and "entityID" in {}) temphot) hottable
                on feed.uuid = hottable.uuid
                ORDER BY hotness desc OFFSET {} LIMIT {}
                """.format(bucket_id, decay, entity_ids_str, offset, limit)
    elif mode == "auto":
        query = """
                SELECT distinct title, "storyID", url, published_date,
                "domain", source_country, entity_name, "entityID",
                "scenarioID", body, "cluster", entities,
                CASE WHEN days = 0 THEN hotness::float
                WHEN "decay" = FALSE THEN hotness::float
                ELSE hotness::float * EXP(-0.01 * days * days)
                END AS hotness from
                (SELECT distinct url, title, "storyID", published_date,
                "domain", source_country, entity_name, "entityID",
                "scenarioID", LEFT(story_body, 400) as body, "cluster", entities,
                hotness->'{}' as hotness,
                current_date - published_date::date as days, {} as "decay"
                FROM feed_autowarehouse
                WHERE published_date > %s AND published_date <= %s
                AND "scenarioID" = '{}' AND "entityID" in {}) hottable
                ORDER BY hotness desc OFFSET {} LIMIT {}
                """.format(bucket_id, decay, scenario_id, entity_ids_str,
                           offset, limit)

    rows = dictfetchall(query, start_date, end_date)
    return rows


def user_entity_bucket(bucket_id, entity_id, scenario_id, dates, mode, page):
    """
    Query to generate feed based on the bucket and the entity.
    """

    entity_id_str = "'{}'".format(entity_id)
    start_date = "'{}'".format(dates[0])
    end_date = "'{}'".format(dates[1])
    decay = dates[2]

    # used for pagination
    limit = COUNT * page
    offset = limit - COUNT

    if mode == "portfolio":
        query = """
                SELECT distinct title, feed."storyID", feed.url, published_date,
                "domain", source_country, entity_name, "entityID",
                "scenarioID", LEFT(story_body, 400), "cluster", entities,
                feed.hotness->'general' AS hotness
                from feed_portfoliowarehouse feed inner join
                (select distinct url, uuid, "storyID",
                CASE WHEN days = 0 THEN hotness::float
                WHEN "decay" = FALSE THEN hotness::float
                ELSE hotness::float * EXP(-0.01 * days * days)
                END AS hotness
                from (select uuid, "storyID", url, hotness->'{}' as hotness,
                current_date - published_date::date as days, {} as "decay"
                from feed_portfoliowarehouse
                where published_date > %s and published_date <= %s
                and "entityID" = {}) temphot) hottable
                on feed.uuid = hottable.uuid
                ORDER BY hotness desc OFFSET {} LIMIT {}
                """.format(bucket_id, decay, entity_id_str, offset, limit)
    elif mode == "auto":
        query = """
                SELECT distinct title, "storyID", url, published_date,
                "domain", source_country, entity_name, "entityID",
                "scenarioID", body, "cluster", entities,
                CASE WHEN days = 0 THEN hotness::float
                WHEN "decay" = FALSE THEN hotness::float
                ELSE hotness::float * EXP(-0.01 * days * days)
                END AS hotness from
                (SELECT distinct url, title, "storyID", published_date,
                "domain", source_country, entity_name, "entityID",
                "scenarioID", LEFT(story_body, 400) as body, "cluster", entities,
                hotness->'{}' as hotness,
                current_date - published_date::date as days, {} as "decay"
                FROM feed_autowarehouse
                WHERE published_date > %s AND published_date <= %s
                AND "scenarioID" = '{}' AND "entityID" = {}) hottable
                ORDER BY hotness desc OFFSET {} LIMIT {}
                """.format(bucket_id, decay, scenario_id, entity_id_str,
                           offset, limit)

    rows = dictfetchall(query, start_date, end_date)
    return rows
