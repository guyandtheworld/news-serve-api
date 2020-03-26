from django.db import connection

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

def get_scenario_entity_count(scenario_id,type_id,n_entities):

    """
    returns list of a entities in a scenario ordered by count, filtered by type 
    if needed
    """

    if n_entities:
        limit = "limit {}".format(n_entities)
    else:
        limit = ""
    if type_id:
        type_filter = """
        inner join
        (select uuid as type_id from apis_storyentityref as sef
        where sef."typeID_id" = '{}') as type
        on entmap."entityID_id" = type.type_id
        """.format(type_id)
    else:
        type_filter = ""

    query = """
    select "entityID_id",count(story_id) as count from apis_storyentitymap as entmap
    {}
    inner join
    (select uuid as story_id from apis_story as story
    where story."scenarioID_id" = '{}') as stry
    on entmap."storyID_id"=stry.story_id
    group by "entityID_id"
    order by count DESC
    {}
    """.format(type_filter,scenario_id,limit)

    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = dictfetchall(cursor)
        return rows
