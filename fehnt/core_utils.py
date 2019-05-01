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
