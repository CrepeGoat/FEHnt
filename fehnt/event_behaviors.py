from fractions import Fraction
from functools import lru_cache

import numpy as np

from fehnt.core_defs import StarPools, StarRatings, Colors, SUMMONS_PER_SESSION
from fehnt.core_utils import multinomial_prob, stone_combinations


class EventDetails:
    """Base class for event details classes."""

    def __init__(self, init_starpool_probs, pool_counts, starpool_counts=None):
        """Construct an instance."""
        self.init_starpool_probs = init_starpool_probs
        self.pool_counts = pool_counts
        self._starpool_counts = (
            pool_counts.iter_group_index(0).apply(np.sum)
            if starpool_counts is None else starpool_counts
        )

    @lru_cache(maxsize=None)
    def starpool_probs(self, prob_tier):
        """
        Generate probabilities for star rating summon pools.

        Calculates by increasing 5-star pools by 0.5% for each tier increase.
        """
        index_inc = np.array([
            idx.star_rating == StarRatings.x5_STAR
            for idx in self.init_starpool_probs.index
        ])
        inc_prob = self.init_starpool_probs[index_inc].sum()
        new_inc_prob = inc_prob + prob_tier*Fraction(1, 200)

        return sf.Series.from_concat([
            self.init_starpool_probs[index_inc] * (new_inc_prob / inc_prob),
            self.init_starpool_probs[~index_inc] * (
                (1-new_inc_prob) / (1-inc_prob)
            ),
        ])

    @lru_cache(maxsize=None)
    def pool_probs(self, prob_tier):
        """Generate probabilities for summon pools."""
        starpool_unit_probs = (
            self.starpool_probs(prob_tier)
            / self._starpool_counts
        )
        return starpool_unit_probs.broadcast_index_to(
            self.pool_counts, level_in_target=0
        ) * self.pool_counts

    @lru_cache(maxsize=None)
    def colorpool_probs(self, prob_tier):
        """Generate probabilities for color summon pools."""
        return (self.pool_probs(prob_tier)
                .iter_group_index(1)
                .apply(np.sum))

    @lru_cache(maxsize=None)
    def color_count_probs(self, prob_tier):
        """Generate probabilities for number of session colors present."""
        color_probs = self.colorpool_probs(prob_tier)
        counts = stone_combinations
        probs = sf.Series([
            multinomial_prob(stone_counts, color_probs)
            for stone_counts in stone_combinations.iter_series(axis=1)
        ], name='probability')
        assert probs.sum() == 1

        return (
            sf.Frame.from_concat([counts, probs], axis=1)
            .set_index_hierarchy(tuple(Colors), drop=True)
            ['probability']
        )

    @classmethod
    def make_standard(cls, pool_counts, starpool_counts=None):
        """Make event behaviors for a standard summoning event."""
        init_starpool_probs = sf.Series.from_items([
            (StarPools.x5_STAR_FOCUS, Fraction(3, 100)),
            (StarPools.x5_STAR, Fraction(3, 100)),
            (StarPools.x4_STAR, Fraction(58, 100)),
            (StarPools.x3_STAR, Fraction(36, 100)),
        ])

        return cls(init_starpool_probs, pool_counts, starpool_counts)

    @classmethod
    def make_legendary(cls, pool_counts, starpool_counts=None):
        """Make event behaviors for a standard summoning event."""
        init_starpool_probs = sf.Series.from_items([
            (StarPools.x5_STAR_FOCUS, Fraction(8, 100)),
            (StarPools.x4_STAR, Fraction(58, 100)),
            (StarPools.x3_STAR, Fraction(34, 100)),
        ])

        return cls(init_starpool_probs, pool_counts, starpool_counts)
