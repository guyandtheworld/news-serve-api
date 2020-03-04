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
        baseScore = baseScore * math.exp(-.2*x*x)
    return baseScore


def get_gross_entity_score(entity_scores):
    """
    Generates Scores for a particular entity by
    * Fetching all grossScore for past N days
    * Decaying score based on timeDiff
    * Aggregating scores for each bucket g1*t1
    * Average of all Buckets
    """
    df = pd.DataFrame(entity_scores)
    df["score"] = df.apply(lambda x: hotness(x['grossScore'], x['timeDiff']), axis=1)
    scores = []
    df.drop(['grossScore', 'timeDiff'], axis=1, inplace=True)
    for entity in df["entityID_id"].unique():
        entity_df = df[df["entityID_id"] == entity]
        bucket_scores = entity_df.groupby(['bucketID_id', "name"])["score"].agg(['sum', 'count'])
        bucket_scores = bucket_scores.reset_index()

        # normalize score by dividing the sum with the amount of articles
        bucket_scores['score'] = np.where(bucket_scores['count'] < 1, \
            bucket_scores['count'], bucket_scores['sum']/bucket_scores['count'])

        # sum all buckets and normalize with bucket count
        gross_entity_score = bucket_scores['score'].sum()/len(bucket_scores)

        obj = {}
        obj["uuid"] = entity
        obj["name"] = bucket_scores["name"].values[0]
        obj["gross_entity_score"] = round(gross_entity_score*1000, 2)
        scores.append(obj)

    return scores
