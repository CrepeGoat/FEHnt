import pytest

from fehnt.core_utils import *


@pytest.mark.parametrize(['n', 'k', 'expt_result'], [
    (0, 0, 1),

    (1, 0, 1),
    (1, 1, 1),

    (2, 0, 1),
    (2, 1, 2),
    (2, 2, 1),

    (3, 0, 1),
    (3, 1, 3),
    (3, 2, 3),
    (3, 3, 1),

    (4, 0, 1),
    (4, 1, 4),
    (4, 2, 6),
    (4, 3, 4),
    (4, 4, 1),
])
def test_nCk(n, k, expt_result):
    assert nCk(n, k) == expt_result


@pytest.fixture
def ppcalc():
    pool_data = [
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
    ]
    pool_counts = (
        pd.DataFrame
        .from_records(pool_data, columns=['star', 'color', 'count'])
        .set_index(['star', 'color'])
        ['count']
    )

    return PoolProbsCalculator(pool_counts)


def test_ppc_starpool(ppcalc):
    for i in range(5):
        starpool = ppcalc.starpool(i)
        assert list(starpool.index) == list(StarPools)
        assert starpool.sum() == 1


def test_ppc_pool(ppcalc):
    from itertools import product

    for i in range(5):
        pool = ppcalc.pool(i)
        assert list(pool.index) == list(product(StarPools, Colors))
        assert pool.sum() == 1


def test_ppc_colorpool(ppcalc):
    for i in range(5):
        colorpool = ppcalc.colorpool(i)
        assert list(colorpool.index) == list(Colors)
        assert colorpool.sum() == 1


def test_stone_combo_prob(ppcalc):
    for i in range(5):
        colorpool = ppcalc.colorpool(i)
        assert sum(
            stone_combo_prob(stones, colorpool)
            for stones in stone_combinations()
        ) == 1


if __name__ == '__main__':
    pytest.main()

