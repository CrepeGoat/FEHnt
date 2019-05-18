import pytest
from unittest import mock
import sympy as sp
import numpy as np

from collections import defaultdict

from fehnt.core import *


@pytest.fixture
def pool_probs():
    value = pd.DataFrame.from_records([
        (StarPools._5_STAR, Colors.RED, 2/24),
        (StarPools._5_STAR, Colors.BLUE, 3/24),
        (StarPools._5_STAR, Colors.GREEN, 3/24),

        (StarPools._4_STAR, Colors.RED, 6/24),
        (StarPools._4_STAR, Colors.BLUE, 5/24),
        (StarPools._4_STAR, Colors.GREEN, 5/24),
    ], columns=['star', 'color', 'probability'])
    assert value['probability'].sum() == 1
    # value['probability'] = sp.symbols('p0:6', nonnegative=True)
    return value.set_index(['star', 'color'])['probability']


@pytest.fixture
def pool_counts():
    value = pd.DataFrame.from_records([
        (StarPools._5_STAR, Colors.RED, 2),
        (StarPools._5_STAR, Colors.BLUE, 2),
        (StarPools._5_STAR, Colors.GREEN, 2),

        (StarPools._4_STAR, Colors.RED, 4),
        (StarPools._4_STAR, Colors.BLUE, 4),
        (StarPools._4_STAR, Colors.GREEN, 4),
    ], columns=['star', 'color', 'count'])
    # value['count'] = sp.symbols('c0:6', nonnegative=True, integer=True)
    return value.set_index(['star', 'color'])['count']


@pytest.fixture
def target_pool_counts():
    value = pd.DataFrame.from_records([
        (StarPools._5_STAR, Colors.RED, 1),
    ], columns=['star', 'color', 'count'])
    # value['count'] = sp.symbols('c0:1', nonnegative=True, integer=True)
    return value.set_index(['star', 'color'])['count']


def test_OutcomeCalculator_init_new_session(monkeypatch):
    # Stubs 1
    stones = (mock.sentinel.stones0,
              mock.sentinel.stones1,
              mock.sentinel.stones2)
    stone_probs = sp.symbols('p0:3', nonnegative=True)
    stone_combos = tuple(zip(stones, stone_probs))

    # Monkey-patches
    monkeypatch.setattr('fehnt.core.sf_ify', lambda x: x)
    monkeypatch.setattr('fehnt.core.stone_combinations',
                        lambda x: (i for i in stone_combos))

    # Stubs 2
    outcome_calc = mock.Mock(spec=OutcomeCalculator,
                             event_details=mock.Mock(),
                             summoner=mock.Mock(),
                             states=defaultdict(int))
    event = EventState(orb_count=mock.sentinel.orb_count,
                       dry_streak=sp.symbols('s'),
                       targets_pulled=mock.sentinel.targets_pulled)
    probability = sp.symbols('p', nonnegative=True)

    # Run test
    OutcomeCalculator.init_new_session(outcome_calc, event, probability)

    # Assert results
    expt_subprobs = [probability * p_i for p_i in stone_probs]

    assert len(outcome_calc.states) == len(expt_subprobs)
    for state, prob in outcome_calc.states.items():
        assert prob in expt_subprobs


def test_OutcomeCalculator_branch_event(monkeypatch, pool_probs, pool_counts,
                                        target_pool_counts):
    # Stubs
    outcome_calc = mock.Mock(spec=OutcomeCalculator,
                             event_details=mock.Mock(pool_counts=pool_counts),
                             summoner=mock.Mock(targets=target_pool_counts),
                             states=defaultdict(int))
    outcome_calc.event_details.pool_probs.return_value = pool_probs
    outcome_calc.event_details.pool_counts.return_value = pool_counts
    event = EventState(orb_count=sp.symbols('orb_count'),
                       dry_streak=sp.symbols('dry_streak'),
                       targets_pulled=0*target_pool_counts)
    session = SessionState(prob_level=1, stone_counts=pd.Series(
        [1, 0, 0], index=[Colors.RED, Colors.BLUE, Colors.GREEN]
    ))
    # probability = sp.symbols('p', nonnegative=True)
    probability = 1/2
    stone_choice = Colors.RED

    # Run test
    OutcomeCalculator.branch_event(outcome_calc, event, session, probability,
                                   stone_choice)

    probs = (1/16, 1/16, 3/8)
    assert len(outcome_calc.states) == len(probs)
    assert sorted(p for p in outcome_calc.states.values()) == sorted(probs)


if __name__ == '__main__':
    pytest.main()
