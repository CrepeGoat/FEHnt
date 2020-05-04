from fractions import Fraction
from functools import lru_cache

import numpy as np
import static_frame as sf

from fehnt.core_defs import StarPools


class EventDetailsBase:
    def __init__(self, pool_counts, starpool_counts=None):
        self.pool_counts = pool_counts
        self._starpool_counts = (
            pool_counts.iter_group_index(0).apply(np.sum)
            if starpool_counts is None else starpool_counts
        )

    def starpool_probs(self, probability_tier=0):
        pass

    @lru_cache(maxsize=None)
    def pool_probs(self, probability_tier=0):
        starpool_unit_probs = (
            self.starpool_probs(probability_tier)
            / self._starpool_counts
        )
        return starpool_unit_probs.broadcast_index_to(
            self.pool_counts, level_in_target=0
        ) * self.pool_counts

    @lru_cache(maxsize=None)
    def colorpool_probs(self, probability_tier=0):
        return (self.pool_probs(probability_tier)
                .iter_group_index(1)
                .apply(np.sum))


# for standard summoning events
class StandardEventDetails(EventDetailsBase):
    @lru_cache(maxsize=None)
    def starpool_probs(self, probability_tier=0):
        i = probability_tier
        return sf.Series.from_items([
            (StarPools._5_STAR_FOCUS, Fraction(12+i, 400)),
            (StarPools._5_STAR, Fraction(12+i, 400)),
            (StarPools._4_STAR, (Fraction(58, 100)
                                 * Fraction(200-(12+i), 200-12))),
            (StarPools._3_STAR, (Fraction(36, 100)
                                 * Fraction(200-(12+i), 200-12))),
        ])


class LegendaryEventDetails(EventDetailsBase):
    @lru_cache(maxsize=None)
    def starpool_probs(self, probability_tier=0):
        i = probability_tier
        return sf.Series.from_items([
            (StarPools._5_STAR_FOCUS, Fraction(16+i, 200)),
            (StarPools._4_STAR, (Fraction(58, 100)
                                 * Fraction(200-(16+i), 200-16))),
            (StarPools._3_STAR, (Fraction(34, 100)
                                 * Fraction(200-(16+i), 200-16))),
        ])
