import math
import pandas as pd
import numpy as np


def hotness(baseScore, timeDiff):
    """
    Defines the aggregate GrossScore for each bucket
    with a time decay, which gives prominence for the
    latest news
    """
    if (timeDiff >= 1):
        x = timeDiff - 1
        baseScore = baseScore * math.exp(-.2 * x * x)
    return baseScore


def get_gross_entity_score(entity_scores):
    """
    Generates Scores for entities in a portfolio by
    * Fetching all grossScore for past N days
    * Decaying score based on timeDiff
    * Aggregating scores for each bucket g1*t1
    * Average of all Buckets
    """
    if len(entity_scores) == 0:
        return []

    df = pd.DataFrame(entity_scores)
    df["score"] = df.apply(lambda x: hotness(x['grossScore'], x['timeDiff']), axis=1)
    scores = []
    df.drop(['grossScore', 'timeDiff'], axis=1, inplace=True)
    for entity in df["entityID_id"].unique():
        entity_df = df[df["entityID_id"] == entity]
        bucket_scores = entity_df.groupby(['bucketID_id', "name", "type", "wikipedia"])[
            "score"].agg(['sum', 'count'])
        bucket_scores = bucket_scores.reset_index()

        # normalize score by dividing the sum with the amount of articles
        bucket_scores['score'] = np.where(bucket_scores['count'] < 1,
                                          bucket_scores['count'], bucket_scores['sum'] / bucket_scores['count'])

        # sum all buckets and normalize with bucket count
        gross_entity_score = bucket_scores['score'].sum() / len(bucket_scores)
        obj = {}
        obj["uuid"] = entity
        obj["name"] = bucket_scores["name"].values[0]
        obj["type"] = bucket_scores["type"].values[0]
        obj["wikipedia"] = bucket_scores["wikipedia"].values[0]
        obj["gross_entity_score"] = round(gross_entity_score * 100, 2)
        scores.append(obj)

    return scores


def get_gross_bucket_scores(bucket_scores):
    """
    Generates Scores for a buckets of a scenario
    * Fetching all grossScore for past N days
    * Decaying score based on timeDiff
    * Aggregating scores for each bucket g1*t1
    * Average of all Buckets
    """
    df = pd.DataFrame(bucket_scores)
    df["score"] = df.apply(lambda x: hotness(x['grossScore'], x['timeDiff']), axis=1)
    df.drop(['grossScore', 'timeDiff'], axis=1, inplace=True)

    bucket_scores = df.groupby(['bucketID_id', "name"])[
        "score"].agg(['sum', 'count'])
    bucket_scores = bucket_scores.reset_index()

    # normalize score by dividing the sum with the amount of articles
    bucket_scores['score'] = np.where(bucket_scores['count'] < 1,
                                      bucket_scores['count'], bucket_scores['sum'] / bucket_scores['count'])

    bucket_scores.drop(["sum", "count"], axis=1, inplace=True)

    bucket_scores["score"] *= 100
    bucket_scores["score"] = bucket_scores["score"].apply(lambda x: round(x, 2))

    bucket_scores.rename(columns={'bucketID_id': 'uuid'}, inplace=True)
    return bucket_scores.to_dict('records')


def get_gross_sentiment_scores(sentiment_scores):
    """
    Generates sentiment for a portfolio
    """
    df = pd.DataFrame(sentiment_scores)
    df["score"] = df.apply(lambda x: hotness(x['sentiment'], x['timeDiff']), axis=1)
    df.drop(['sentiment', 'timeDiff'], axis=1, inplace=True)

    sentiment_scores = df.groupby(['entityID_id', "name"])[
        "score"].agg(['sum', 'count'])
    sentiment_scores = sentiment_scores.reset_index()

    # normalize score by dividing the sum with the amount of articles
    sentiment_scores['score'] = sentiment_scores['sum'] / sentiment_scores['count']

    sentiment_scores.drop(["sum", "count"], axis=1, inplace=True)

    sentiment_scores["score"] *= 100
    sentiment_scores["score"] = sentiment_scores["score"].apply(
        lambda x: round(x, 2))

    sentiment_scores.columns = ['uuid', 'name', 'sentiment']
    return sentiment_scores.to_dict('records')
