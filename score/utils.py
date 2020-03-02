import math


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
