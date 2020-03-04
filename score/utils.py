import math
import pandas as pd


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


def convert_to_scores(entity_scores):
    """
    """
    df = pd.DataFrame(entity_scores)
    df["score"] = df.apply(lambda x: hotness(x['grossScore'], x['timeDiff']), axis=1)
    scores = {}
    for entity in df["entityID_id"].unique():
        bucket_scores = df[df["entityID_id"] == entity].groupby('bucketID_id').sum()
        bucket_scores = bucket_scores.reset_index()
        print(bucket_scores)
        gross_entity_score = bucket_scores['score'].sum()/len(bucket_scores)
        print(gross_entity_score)
        scores[df[df["entityID_id"] == entity]["name"].values[0]] = gross_entity_score

    print(scores)
