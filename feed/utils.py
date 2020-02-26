import json
import math

import pandas as pd

from datetime import datetime, timedelta


KEYWORD_SCORE = 30


def similarity(str1, str2):
    if str1 in str2:
        return KEYWORD_SCORE
    else:
        return 0


def presence_score(keyword, analytics, analytics_type):
    """
    gives score to the article based on the presence of
    relevant keyword in the content and the body
    """
    all_entities = []
    for i in analytics['entities']:
        all_entities = all_entities + analytics['entities'][i]

    score = 0
    for term in all_entities:
        score = similarity(keyword, term.lower())
        if score > 0:
            break

    if analytics_type == 'title':
        return score*2
    else:
        return score


def hotness(article):
    """
    adding to score if the company term is in title
    * domain score - domain reliability
    """
    s = article.title_analytics["vader_sentiment_score"]["compound"]

    keyword = article["search_keyword"].lower()

    # negative news
    s = -s*100

    # presence of keyword in title
    s += presence_score(keyword, article["title_analytics"], "title")

    # presence of keyword in body
    s += presence_score(keyword, article["body_analytics"], "body")

    baseScore = math.log(max(s, 1))

    timeDiff = (datetime.now() - article["published_date"]).days

    # number of months
    timeDiff = timeDiff // 30

    if (timeDiff >= 1):
        x = timeDiff - 1
        baseScore = baseScore * math.exp(-.2*x*x)

    return baseScore


def score_in_bulk(articles):
    """
    convert db object into dictionary and cleans
    and scores the data
    * return sample shouldn't be skewed towards one company
    """
    df = pd.DataFrame(list(articles))

    df["hotness"] = df.apply(hotness, axis=1)

    # use unique hash to eliminate duplicates
    # eventually, we'll need to score each domain
    # and only keep the most reliable source and
    # eliminate others
    df.drop_duplicates("unique_hash", inplace=True)
    df.drop_duplicates("title", inplace=True)

    df = df.sort_values(['hotness'], ascending=False)
    result_sample = df.head(200)
    result_sample['_id'] = result_sample['_id'].apply(str)
    return result_sample.to_dict(orient='records')
