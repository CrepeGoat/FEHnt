from fehnt.core_defs import *

from collections import namedtuple
from fractions import Fraction
from functools import lru_cache

# TODO use static_frame instead
import pandas as pd


def nCk(n, k):
    result = 1
    for i in range(k):
        result = (result * (n-i)) // (i+1)
    return result


EventState = namedtuple('EventState', 'orb_count dry_streak targets_pulled')
SessionState = namedtuple('SessionState', 'prob_level stone_counts')


class StateStruct(namedtuple('_', 'event session')):
    def _obj_func(self):
        return (self.event.orb_count, -self.session.stone_counts.sum())

    def __lt__(self, other):
        return self._obj_func() < other._obj_func()


ResultState = namedtuple('ResultState', 'orb_count targets_pulled')


class PoolProbsCalculator:
    def __init__(self, pool_counts, starpool_counts=None):
        self.pool_counts = pool_counts
        self.starpool_counts = (
            pool_counts.groupby(level='star', sort=False).sum()
            if starpool_counts is None else starpool_counts
        )

    @lru_cache(maxsize=None)
    def starpool(self, probability_tier=0):
        i = probability_tier
        return pd.DataFrame.from_records([
            (StarPools._5_STAR_FOCUS, Fraction(12+i, 400)),
            (StarPools._5_STAR, Fraction(12+i, 400)),
            (StarPools._4_STAR, (Fraction(58, 100)
                                 * Fraction(200-(12+i), 200-12))),
            (StarPools._3_STAR, (Fraction(36, 100)
                                 * Fraction(200-(12+i), 200-12))),
        ], columns=['star', 'probability']).set_index('star')['probability']

    @lru_cache(maxsize=None)
    def pool(self, probability_tier=0):
        return self.pool_counts.mul(
            self.starpool(probability_tier) / self.starpool_counts,
            level='star'
        )

    @lru_cache(maxsize=None)
    def colorpool(self, probability_tier=0):
        return (self.pool(probability_tier)
                .groupby(level='color', sort=False)
                .sum())


def stone_combo_prob(stone_counts, color_probs):
    no_summons = stone_counts.sum()
    stones_remaining = no_summons - (stone_counts.cumsum()-stone_counts)

    return (color_probs[stone_counts.index] ** stone_counts
            * stones_remaining.combine(stone_counts, nCk)
            ).prod()


# @lru_cache(maxsize=None)
def stone_combinations(color_probs):
    return ((s, stone_combo_prob(s, color_probs))
            for _, s in stone_combinations.cache.iterrows())


stone_combinations.cache = pd.DataFrame.from_records([
    (i, j, k, summons_per_session-i-j-k)
    for i in range(summons_per_session+1)
    for j in range(summons_per_session+1-i)
    for k in range(summons_per_session+1-i-j)
], columns=Colors)


