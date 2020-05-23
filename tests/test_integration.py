from fractions import Fraction

import pytest

from fehnt.core import *
from fehnt.core_utils import make_pool_counts


def test_run():
    # (based on Heroes of Gallia summoning event)
    pool_counts = make_pool_counts(
        (StarPools.x5_STAR_FOCUS, Colors.RED, 1),
        (StarPools.x5_STAR_FOCUS, Colors.BLUE, 1),
        (StarPools.x5_STAR_FOCUS, Colors.GREEN, 1),
        (StarPools.x5_STAR_FOCUS, Colors.GRAY, 1),

        (StarPools.x5_STAR, Colors.RED, 19),
        (StarPools.x5_STAR, Colors.BLUE, 15),
        (StarPools.x5_STAR, Colors.GREEN, 15),
        (StarPools.x5_STAR, Colors.GRAY, 8),

        (StarPools.x4_STAR, Colors.RED, 32),
        (StarPools.x4_STAR, Colors.BLUE, 30),
        (StarPools.x4_STAR, Colors.GREEN, 20),
        (StarPools.x4_STAR, Colors.GRAY, 28),

        (StarPools.x3_STAR, Colors.RED, 32),
        (StarPools.x3_STAR, Colors.BLUE, 29),
        (StarPools.x3_STAR, Colors.GREEN, 19),
        (StarPools.x3_STAR, Colors.GRAY, 28),
    )

    target_pool_counts = make_pool_counts(
        (StarPools.x5_STAR_FOCUS, Colors.RED, 1),
    )

    outcome_probs = OutcomeCalculator(
        event_details=StandardEventDetails(pool_counts),
        summoner=ColorHuntSummoner(target_pool_counts),
    )(no_of_orbs=10)

    assert outcome_probs[5, make_pool_counts(
        (StarPools.x5_STAR_FOCUS, Colors.RED, 1)
    )] == Fraction(53331461890648098721, 2529964800000000000000)

    assert outcome_probs[1, make_pool_counts(
        (StarPools.x5_STAR_FOCUS, Colors.RED, 1)
    )] == Fraction(1803428037031254581, 158122800000000000000)

    assert outcome_probs[1, make_pool_counts(
        (StarPools.x5_STAR_FOCUS, Colors.RED, 0)
    )] == Fraction(8492342626380177821929, 19567696500000000000000)

    assert outcome_probs[0, make_pool_counts(
        (StarPools.x5_STAR_FOCUS, Colors.RED, 1)
    )] == Fraction(
        35632905572024260525584546495453381641543009,
        3168357335173324800000000000000000000000000000
    )

    assert outcome_probs[0, make_pool_counts(
        (StarPools.x5_STAR_FOCUS, Colors.RED, 0)
    )] == Fraction(
        1654738849167994100960528289363746618358456991,
        3168357335173324800000000000000000000000000000
    )


if __name__ == '__main__':
    pytest.main()
