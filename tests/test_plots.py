from fractions import Fraction

import pytest

from fehnt.plots import *
from fehnt.core_defs import StarPools, Colors
from fehnt.core_utils import ResultState, make_pool_counts


def test_count_pulls():
    outcomes = {
        ResultState(orbs_spent=5, targets_pulled=make_pool_counts(
            (StarPools.x5_STAR_FOCUS, Colors.RED, 1)
        )): Fraction(53331461890648098721, 2529964800000000000000),

        ResultState(orbs_spent=9, targets_pulled=make_pool_counts(
            (StarPools.x5_STAR_FOCUS, Colors.RED, 1)
        )): Fraction(1803428037031254581, 158122800000000000000),

        ResultState(orbs_spent=9, targets_pulled=make_pool_counts(
            (StarPools.x5_STAR_FOCUS, Colors.RED, 0)
        )): Fraction(8492342626380177821929, 19567696500000000000000),

        ResultState(orbs_spent=10, targets_pulled=make_pool_counts(
            (StarPools.x5_STAR_FOCUS, Colors.RED, 1)
        )): Fraction(
            35632905572024260525584546495453381641543009,
            3168357335173324800000000000000000000000000000
        ),

        ResultState(orbs_spent=10, targets_pulled=make_pool_counts(
            (StarPools.x5_STAR_FOCUS, Colors.RED, 0)
        )): Fraction(
            1654738849167994100960528289363746618358456991,
            3168357335173324800000000000000000000000000000
        ),
    }

    assert count_pulls(outcomes) == [0.95626834828473, 0.04373165171527006]
