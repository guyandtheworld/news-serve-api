from .sql import get_scenario_entity_count

def get_story_entity_counts(scenario_id, type_id = None, n_entities = None):
    """
    return the top n entities by number of times they appear in the stories
    pass type_id to filter by entity type
    pass n_entities to specify amount of entities to return, leave blank for
    every entity
    """
    data = get_scenario_entity_count(scenario_id,type_id,n_entities)
    return data
