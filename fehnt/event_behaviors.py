from fehnt.core_defs import *

from fractions import Fraction
from functools import lru_cache

# TODO use static_frame instead
import pandas as pd


def nCk(n, k):
    result = 1
    for i in range(k):
        result = (result * (n-i)) // (i+1)
    return result


class EventDetailsBase:
    def __init__(self, pool_counts, starpool_counts=None):
        self.pool_counts = pool_counts
        self._starpool_counts = (
            pool_counts.groupby(level='star', sort=False).sum()
            if starpool_counts is None else starpool_counts
        )

    def starpool_probs(self, probability_tier=0):
        pass

    @lru_cache(maxsize=None)
    def pool_probs(self, probability_tier=0):
        return self.pool_counts.mul(
            self.starpool_probs(probability_tier) / self._starpool_counts,
            level='star'
        )

    @lru_cache(maxsize=None)
    def colorpool_probs(self, probability_tier=0):
        return (self.pool_probs(probability_tier)
                .groupby(level='color', sort=False)
                .sum())


# for standard summoning events
class StandardEventDetails(EventDetailsBase):
    @lru_cache(maxsize=None)
    def starpool_probs(self, probability_tier=0):
        i = probability_tier
        return pd.DataFrame.from_records([
            (StarPools._5_STAR_FOCUS, Fraction(12+i, 400)),
            (StarPools._5_STAR, Fraction(12+i, 400)),
            (StarPools._4_STAR, (Fraction(58, 100)
                                 * Fraction(200-(12+i), 200-12))),
            (StarPools._3_STAR, (Fraction(36, 100)
                                 * Fraction(200-(12+i), 200-12))),
        ], columns=['star', 'probability']).set_index('star')['probability']


class LegendaryEventDetails(EventDetailsBase):
    @lru_cache(maxsize=None)
    def starpool_probs(self, probability_tier=0):
        i = probability_tier
        return pd.DataFrame.from_records([
            (StarPools._5_STAR_FOCUS, Fraction(16+i, 200)),
            (StarPools._4_STAR, (Fraction(58, 100)
                                 * Fraction(200-(16+i), 200-16))),
            (StarPools._3_STAR, (Fraction(34, 100)
                                 * Fraction(200-(16+i), 200-16))),
        ], columns=['star', 'probability']).set_index('star')['probability']
