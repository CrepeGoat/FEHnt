from fractions import Fraction

import pytest

from fehnt.core import *
from fehnt.core_utils import make_pool_counts


def test_run():
    # (based on Heroes of Gallia summoning event)
    pool_counts = make_pool_counts(
        (StarPools._5_STAR_FOCUS, Colors.RED, 1),
        (StarPools._5_STAR_FOCUS, Colors.BLUE, 1),
        (StarPools._5_STAR_FOCUS, Colors.GREEN, 1),
        (StarPools._5_STAR_FOCUS, Colors.GRAY, 1),

        (StarPools._5_STAR, Colors.RED, 19),
        (StarPools._5_STAR, Colors.BLUE, 15),
        (StarPools._5_STAR, Colors.GREEN, 15),
        (StarPools._5_STAR, Colors.GRAY, 8),

        (StarPools._4_STAR, Colors.RED, 32),
        (StarPools._4_STAR, Colors.BLUE, 30),
        (StarPools._4_STAR, Colors.GREEN, 20),
        (StarPools._4_STAR, Colors.GRAY, 28),

        (StarPools._3_STAR, Colors.RED, 32),
        (StarPools._3_STAR, Colors.BLUE, 29),
        (StarPools._3_STAR, Colors.GREEN, 19),
        (StarPools._3_STAR, Colors.GRAY, 28),
    )

    target_pool_counts = make_pool_counts(
        (StarPools._5_STAR_FOCUS, Colors.RED, 1),
    )

    outcome_probs = dict(condense_results(OutcomeCalculator(
        event_details=StandardEventDetails(pool_counts),
        summoner=ColorHuntSummoner(target_pool_counts),
    )(no_of_orbs=10)))

    assert outcome_probs[make_pool_counts(
        (StarPools._5_STAR_FOCUS, Colors.RED, 1)
    )] == Fraction(
        138557499491321015377325272287453381641543009,
        3168357335173324800000000000000000000000000000
    )
    assert outcome_probs[make_pool_counts(
        (StarPools._5_STAR_FOCUS, Colors.RED, 0)
    )] == Fraction(
        3029799835682003784622674727712546618358456991,
        3168357335173324800000000000000000000000000000
    )


if __name__ == '__main__':
    pytest.main()
