import pytest

from fehnt.core_utils import *

from fractions import Fraction


@pytest.mark.parametrize(['k_array', 'expt_result'], [
    ((0,), 1),

    ((0, 1), 1),
    ((1, 0), 1),

    ((0, 2), 1),
    ((1, 1), 2),
    ((2, 0), 1),

    ((0, 3), 1),
    ((1, 2), 3),
    ((2, 1), 3),
    ((3, 0), 1),

    ((0, 4), 1),
    ((1, 3), 4),
    ((2, 2), 6),
    ((3, 1), 4),
    ((4, 0), 1),
])
def test_nCkarray(k_array, expt_result):
    assert nCkarray(k_array) == expt_result


@pytest.mark.parametrize(['counts', 'prob_ratios', 'expt_result'], [
    ((0, 0), (1, 1), 1),

    ((0, 1), (1, 1), Fraction(1, 2)),
    ((1, 0, 0), (1, 1, 0), Fraction(1, 2)),

    ((2, 0), (1, 1), Fraction(1, 4)),

    ((1, 0, 1), (1, 1, 1), Fraction(2, 9)),
])
def test_n_nomial_prob(counts, prob_ratios, expt_result):
    denom = sum(prob_ratios)
    probs = tuple(Fraction(i, denom) for i in prob_ratios)

    counts = sf.Series(counts)
    probs = sf.Series(probs)

    assert n_nomial_prob(counts, probs) == expt_result


if __name__ == '__main__':
    pytest.main()
