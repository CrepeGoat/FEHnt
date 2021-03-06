import pytest

from fehnt.summoner_behaviors import *
from fehnt.core_defs import Colors, StarPools
from fehnt.core_utils import make_pool_counts


@pytest.fixture
def pool_counts():
    # (based on Heroes of Gallia summoning event)
    return make_pool_counts(
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


@pytest.mark.parametrize('summoner, targets_pulled, expt_result', [
    (
        BlindFullSummoner(target_pool_counts=make_pool_counts(
            (StarPools.x5_STAR_FOCUS, Colors.RED, 1),
        )),
        make_pool_counts(
            (StarPools.x5_STAR_FOCUS, Colors.BLUE, 1),
        ),
        True,
    ),
    (
        BlindFullSummoner(target_pool_counts=make_pool_counts(
            (StarPools.x5_STAR_FOCUS, Colors.RED, 1),
        )),
        make_pool_counts(
            (StarPools.x5_STAR_FOCUS, Colors.RED, 1),
        ),
        False,
    ),

    (
        BlindFullSummoner(target_pool_counts=make_pool_counts(
            (StarPools.x5_STAR_FOCUS, Colors.RED, 1),
            (StarPools.x5_STAR_FOCUS, Colors.BLUE, 1),
        )),
        make_pool_counts(
            (StarPools.x5_STAR_FOCUS, Colors.RED, 1),
        ),
        True,
    ),
    (
        BlindFullSummoner(target_pool_counts=make_pool_counts(
            (StarPools.x5_STAR_FOCUS, Colors.RED, 1),
            (StarPools.x5_STAR_FOCUS, Colors.BLUE, 1),
        )),
        make_pool_counts(
            (StarPools.x5_STAR_FOCUS, Colors.BLUE, 1),
        ),
        True,
    ),
    (
        BlindFullSummoner(target_pool_counts=make_pool_counts(
            (StarPools.x5_STAR_FOCUS, Colors.RED, 1),
            (StarPools.x5_STAR_FOCUS, Colors.BLUE, 1),
        )),
        make_pool_counts(
            (StarPools.x5_STAR_FOCUS, Colors.RED, 1),
            (StarPools.x5_STAR_FOCUS, Colors.BLUE, 1),
        ),
        False,
    ),

    #--------------------------------------------------------------------------

    (
        ColorHuntSummoner(target_pool_counts=make_pool_counts(
            (StarPools.x5_STAR_FOCUS, Colors.RED, 1),
        )),
        make_pool_counts(
            (StarPools.x5_STAR_FOCUS, Colors.BLUE, 1),
        ),
        True,
    ),
    (
        ColorHuntSummoner(target_pool_counts=make_pool_counts(
            (StarPools.x5_STAR_FOCUS, Colors.RED, 1),
        )),
        make_pool_counts(
            (StarPools.x5_STAR_FOCUS, Colors.RED, 1),
        ),
        False,
    ),

    (
        ColorHuntSummoner(target_pool_counts=make_pool_counts(
            (StarPools.x5_STAR_FOCUS, Colors.RED, 1),
            (StarPools.x5_STAR_FOCUS, Colors.BLUE, 1),
        )),
        make_pool_counts(
            (StarPools.x5_STAR_FOCUS, Colors.RED, 1),
        ),
        True,
    ),
    (
        ColorHuntSummoner(target_pool_counts=make_pool_counts(
            (StarPools.x5_STAR_FOCUS, Colors.RED, 1),
            (StarPools.x5_STAR_FOCUS, Colors.BLUE, 1),
        )),
        make_pool_counts(
            (StarPools.x5_STAR_FOCUS, Colors.BLUE, 1),
        ),
        True,
    ),
    (
        ColorHuntSummoner(target_pool_counts=make_pool_counts(
            (StarPools.x5_STAR_FOCUS, Colors.RED, 1),
            (StarPools.x5_STAR_FOCUS, Colors.BLUE, 1),
        )),
        make_pool_counts(
            (StarPools.x5_STAR_FOCUS, Colors.RED, 1),
            (StarPools.x5_STAR_FOCUS, Colors.BLUE, 1),
        ),
        False,
    ),
])
def test_should_start_new_session(summoner, targets_pulled, expt_result):
    assert summoner.should_start_new_session(targets_pulled) == expt_result
