from fractions import Fraction
from functools import lru_cache

import numpy as np
import static_frame as sf

from fehnt.core_defs import StarPools, Colors, SUMMONS_PER_SESSION
from fehnt.core_utils import multinomial_prob, stone_combinations


class EventDetailsBase:
    """Base class for event details classes."""

    def __init__(self, pool_counts, starpool_counts=None):
        """Construct an instance."""
        self.pool_counts = pool_counts
        self._starpool_counts = (
            pool_counts.iter_group_index(0).apply(np.sum)
            if starpool_counts is None else starpool_counts
        )

    def starpool_probs(self, prob_tier):
        """Generate probabilities for star rating summon pools."""
        raise NotImplementedError

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

    @lru_cache(maxsize=None)
    def min_color_count_probs(self, prob_tier):
        """Generate probabilities for minimum session colors present."""
        counts_table = self.color_count_probs(prob_tier)
        min_counts_seq = [
            (i, j, k, l)
            for i in range(SUMMONS_PER_SESSION+1)
            for j in range(SUMMONS_PER_SESSION+1-i)
            for k in range(SUMMONS_PER_SESSION+1-i-j)
            for l in range(SUMMONS_PER_SESSION+1-i-j-k)
        ]
        min_counts_index = sf.Frame.from_records(
            min_counts_seq, columns=tuple(Colors)
        ).set_index_hierarchy(tuple(Colors), drop=False).index

        probs = sf.Series([
            counts_table[(counts_table.index >= min_counts).all(axis=1)].sum(axis=0)
            for min_counts in min_counts_index
        ], index=min_counts_index, name='probability')

        return probs


# for standard summoning events
class StandardEventDetails(EventDetailsBase):
    """A representation of event behaviors in a standard summoning event."""

    @lru_cache(maxsize=None)
    def starpool_probs(self, prob_tier):
        """Generate probabilities for star rating summon pools."""
        i = prob_tier
        return sf.Series.from_items([
            (StarPools._5_STAR_FOCUS, Fraction(12+i, 400)),
            (StarPools._5_STAR, Fraction(12+i, 400)),
            (StarPools._4_STAR, (Fraction(58, 100)
                                 * Fraction(200-(12+i), 200-12))),
            (StarPools._3_STAR, (Fraction(36, 100)
                                 * Fraction(200-(12+i), 200-12))),
        ])


class LegendaryEventDetails(EventDetailsBase):
    """A representation of event behaviors in a legendary summoning event."""

    @lru_cache(maxsize=None)
    def starpool_probs(self, prob_tier):
        """Generate probabilities for star rating summon pools."""
        i = prob_tier
        return sf.Series.from_items([
            (StarPools._5_STAR_FOCUS, Fraction(16+i, 200)),
            (StarPools._4_STAR, (Fraction(58, 100)
                                 * Fraction(200-(16+i), 200-16))),
            (StarPools._3_STAR, (Fraction(34, 100)
                                 * Fraction(200-(16+i), 200-16))),
        ])
