import math
import pandas as pd
import re

from datetime import datetime
from .sql import story_entities


KEYWORD_SCORE = 20


def similarity(keyword, text):
    """
    Generates score based on the number of times keywords
    appear on the text body
    """
    count = sum(1 for _ in re.finditer(r'\b%s\b' % re.escape(keyword), text))
    return count * KEYWORD_SCORE


def presence_score(keyword, text, analytics_type):
    """
    Gives score to the article based on the presence of
    relevant keyword in the content and the body
    """
    score = similarity(keyword, text)

    if analytics_type == 'title':
        return score * 2
    else:
        return score


def hotness(article, bucket, sentiment, mode):
    """
    adding to score if the company term is in title
    * domain score - domain reliability
    """
    title_sentiment = article["title_sentiment"]["compound"]
    body_sentiment = article["body_sentiment"]["compound"]

    s = (title_sentiment + body_sentiment) / 2

    if mode == "portfolio":
        keyword = article["search_keyword"]
    else:
        keyword = article["name"]

    if sentiment:
        # negative news
        s = -s * 30 + 30

    # presence of keyword in title
    s += presence_score(keyword.lower(), article["title"].lower(), "title")

    # presence of keyword in body
    s += presence_score(keyword.lower(), article["body"].lower(), "body")

    if bucket:
        # bucket score + source score
        s += (article["grossScore"] * 50)

    baseScore = math.log(max(s, 1))

    return round(baseScore, 3)


def score_in_bulk(articles, bucket=False, sentiment=True, mode="portfolio"):
    """
    convert db object into dictionary and cleans
    and scores the data
    * return sample shouldn't be skewed towards one company
    """
    df = pd.DataFrame(list(articles))

    df["published_date"] = df["published_date"].dt.tz_localize(None)
    df["hotness"] = df.apply(lambda x: hotness(x, bucket, sentiment, mode), axis=1)

    # use unique hash to eliminate duplicates
    df.drop_duplicates("unique_hash", inplace=True)
    df.drop(["body_sentiment", "title_sentiment", "unique_hash",
             "search_keyword"], axis=1, inplace=True)
    df = df.sort_values(['hotness'], ascending=False)
    result_sample = df.head(50)
    result_sample['uuid'] = result_sample['uuid'].apply(str)
    result_sample['entityID_id'] = result_sample['entityID_id'].apply(str)
    result_sample = result_sample.fillna(False)
    result_sample["body"] = result_sample["body"].str[:400]

    return result_sample.to_dict(orient='records')


def attach_story_entities(processed_stories):
    """
    Take in a list of 'processed' stories
    and return the entities found in those stories
    """
    story_ids = [story['uuid'] for story in processed_stories]
    temp_entities = story_entities(story_ids)

    if len(temp_entities) == 0:
        return processed_stories

    story_ent = pd.DataFrame(temp_entities).astype(str)\
        .set_index('uuid').rename({"entityID_id": "entity_id"}, axis=1)

    d = {}

    for i in story_ent['storyID_id'].unique():
        d[i] = story_ent[story_ent['storyID_id'] == i].drop(['storyID_id'], axis=1)\
            .to_dict('records')

    for story in processed_stories:
        try:
            story['entities'] = d[story['uuid']]
        except Exception:
            story['entities'] = {}

    return processed_stories
