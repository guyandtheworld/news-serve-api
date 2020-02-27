import math

import pandas as pd

from datetime import datetime, timedelta


KEYWORD_SCORE = 30


def similarity(str1, str2):
    if str1 in str2:
        return KEYWORD_SCORE
    else:
        return 0


def presence_score(keyword, text, analytics_type):
    """
    gives score to the article based on the presence of
    relevant keyword in the content and the body
    """
    score = similarity(keyword, text)

    if analytics_type == 'title':
        return score*2
    else:
        return score


def hotness(article):
    """
    adding to score if the company term is in title
    * domain score - domain reliability
    """
    s = article["title_sentiment"]["compound"]

    keyword = article["search_keyword"]

    # negative news
    s = -s*100

    # presence of keyword in title
    s += presence_score(keyword.lower(), article["title"].lower(), "title")

    # presence of keyword in body
    s += presence_score(keyword.lower(), article["body"].lower(), "body")

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

    df["published_date"] = df["published_date"].dt.tz_localize(None)
    df["hotness"] = df.apply(hotness, axis=1)

    # use unique hash to eliminate duplicates
    df.drop_duplicates("unique_hash", inplace=True)
    df.drop_duplicates("title", inplace=True)

    df = df.sort_values(['hotness'], ascending=False)
    result_sample = df.head(200)
    result_sample['uuid'] = result_sample['uuid'].apply(str)
    return result_sample.to_dict(orient='records')
