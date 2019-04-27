from fehnt.core_defs import *

from collections import namedtuple
from fractions import Fraction

# TODO use static_frame instead
import pandas as pd


def nCk(n, k):
    result = 1
    for i in range(k):
        result = (result * (n-i)) // (i+1)
    return result


EventState = namedtuple('EventState', 'orb_count dry_streak targets_pulled')
SessionState = namedtuple('SessionState', 'prob_level stone_counts')
ResultState = namedtuple('ResultState', 'orb_count targets_pulled')


class PoolProbsCalculator:
    def __init__(self, pool_counts, starpool_counts=None):
        self.pool_counts = pool_counts
        self.starpool_counts = (
            pool_counts.groupby(level='star', sort=False).sum()
            if starpool_counts is None else starpool_counts
        )

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

    def pool(self, probability_tier=0):
        return self.pool_counts.mul(
            self.starpool(probability_tier) / self.starpool_counts,
            level='star'
        )

    def colorpool(self, probability_tier=0):
        return (self.pool(probability_tier)
                .groupby(level='color', sort=False)
                .sum())


stone_combos = [pd.Series((i, j, k, summons_per_session-i-j-k), index=Colors)
                for i in range(summons_per_session+1)
                for j in range(summons_per_session+1-i)
                for k in range(summons_per_session+1-i-j)]

def stone_combinations():
    return (i for i in stone_combos)


def stone_combo_prob(stone_counts, color_probs):
    no_summons = stone_counts.sum()
    stones_remaining = no_summons - (stone_counts.cumsum()-stone_counts)

    return (color_probs[stone_counts.index] ** stone_counts
            * stones_remaining.combine(stone_counts, nCk)
            ).prod()
