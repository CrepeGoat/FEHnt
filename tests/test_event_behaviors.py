import pytest

from fehnt.event_behaviors import *
from fehnt.core_defs import Colors, StarPools


@pytest.fixture
def standard_event_details():
    pool_data = [
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
    ]
    pool_counts = (
        sf.Frame
        .from_records(pool_data, columns=['star', 'color', 'count'])
        .set_index_hierarchy(['star', 'color'])
        ['count']
    )

    return EventDetails.make_standard(pool_counts)


def test_standard_event_starpool_probs(standard_event_details):
    for i in range(5):
        starpool = standard_event_details.starpool_probs(i)
        assert set(starpool.index) <= set(StarPools)
        assert starpool.sum() == 1


def test_standard_event_pool_probs(standard_event_details):
    from itertools import product

    for i in range(5):
        pool = standard_event_details.pool_probs(i)
        assert set(tuple(i) for i in pool.index) <= set(product(StarPools, Colors))
        assert pool.sum() == 1


def test_standard_event_colorpool_probs(standard_event_details):
    for i in range(5):
        colorpool = standard_event_details.colorpool_probs(i)
        assert set(colorpool.index) <= set(Colors)
        assert colorpool.sum() == 1


if __name__ == '__main__':
    pytest.main()
