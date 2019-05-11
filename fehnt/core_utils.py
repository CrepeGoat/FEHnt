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


def n_nomial_prob(counts, probs):
    total_count = counts.sum()
    remaining_counts = total_count - (counts.cumsum()-counts)

    return (probs[counts.index] ** counts
            * remaining_counts.combine(counts, nCk)
            ).prod()


# @lru_cache(maxsize=None)
def stone_combinations(color_probs):
    return ((s, n_nomial_prob(counts=s, probs=color_probs))
            for _, s in stone_combinations.cache.iterrows())


stone_combinations.cache = pd.DataFrame.from_records([
    (i, j, k, summons_per_session-i-j-k)
    for i in range(summons_per_session+1)
    for j in range(summons_per_session+1-i)
    for k in range(summons_per_session+1-i-j)
], columns=Colors)
