from fehnt.core_defs import *

from collections import namedtuple
from fractions import Fraction
from functools import lru_cache
from itertools import chain

# TODO use static_frame instead
import numpy as np
import static_frame as sf
import pandas as pd


def nCkarray(n, k_array):
    result = 1
    for i, j in enumerate(chain(*(range(k) for k in k_array))):
        result = (result * (n-i)) // (j+1)
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

    return (nCkarray(no_summons, stone_counts.values)
            * (color_probs[stone_counts.index] ** stone_counts).prod())


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
