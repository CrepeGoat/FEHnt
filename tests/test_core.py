import pytest
from unittest import mock
import sympy as sp
import numpy as np

from collections import defaultdict

from fehnt.core import *


@pytest.fixture
def pool_probs():
    value = pd.DataFrame.from_records([
        ('5', 'red', 3/32),
        ('5', 'blue', 4/32),
        ('5', 'green', 4/32),

        ('4', 'red', 7/32),
        ('4', 'blue', 7/32),
        ('4', 'green', 7/32),
    ], columns=['star', 'color', 'probability'])
    # value['probability'] = sp.symbols('p0:6', nonnegative=True)
    return value.set_index(['star', 'color'])['probability']


@pytest.fixture
def pool_counts():
    value = pd.DataFrame.from_records([
        ('5', 'red', 2),
        ('5', 'blue', 2),
        ('5', 'green', 2),

        ('4', 'red', 4),
        ('4', 'blue', 4),
        ('4', 'green', 4),
    ], columns=['star', 'color', 'count'])
    # value['count'] = sp.symbols('c0:6', nonnegative=True, integer=True)
    return value.set_index(['star', 'color'])['count']


@pytest.fixture
def target_pool_counts():
    value = pd.DataFrame.from_records([
        ('5', 'red', 1),
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


if __name__ == '__main__':
    pytest.main()
