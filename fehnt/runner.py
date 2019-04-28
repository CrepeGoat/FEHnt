from .core_defs import *
from .core_utils import *
from .pd_sf_convert import *
from .summon_behaviors import *

from collections import defaultdict
from fractions import Fraction

import pandas as pd
import sortedcontainers as sc


class DefaultSortedDict(sc.SortedDict):
    def __missing__(self, key):
        return Fraction()


def get_outcomes(no_of_orbs, summon_behavior):
    # Inputs (hard-coded for now)
    # (based on Heroes of Gallia summoning event)
    pool_counts = pd.DataFrame.from_records([
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
    ], columns=['star', 'color', 'count'], index=['star', 'color'])['count']

    target_pool_counts = pd.DataFrame.from_records([
        (StarPools._5_STAR_FOCUS, Colors.RED, 1),
    ], columns=['star', 'color', 'count'], index=['star', 'color'])['count']

    states = DefaultSortedDict()
    outcomes = defaultdict(Fraction, [])

    ppcalc = PoolProbsCalculator(pool_counts)
    stone_chooser = summon_behavior(target_pool_counts)

    def init_new_session(event, probability):
        prob_tier = event.dry_streak // summons_per_session
        color_probs = ppcalc.colorpool(prob_tier)

        for stones, stones_prob in stone_combinations(color_probs):
            states[StateStruct(
                sf_ify(event),
                sf_ify(SessionState(prob_tier, stones))
            )] += probability * stones_prob

    def branch_event(event, session, prob, stone_choice):
        new_session = session._replace(stone_counts=session.stone_counts.sub(
            pd.Series([1], index=[stone_choice]), fill_value=0
        ))
        orb_count = event.orb_count - stone_cost(session.stone_counts.sum())

        choice_starpool_probs = (ppcalc
                                 .pool(session.prob_level)
                                 .xs(stone_choice, level='color'))
        choice_starpool_probs /= choice_starpool_probs.sum()

        for starpool, subprob in choice_starpool_probs.iteritems():
            total_prob = prob * subprob

            if starpool in (StarPools._5_STAR_FOCUS, StarPools._5_STAR):
                dry_streak = 0
            else:
                dry_streak = event.dry_streak + 1

            if (starpool, stone_choice) in target_pool_counts.index:
                targets_pulled = event.targets_pulled.copy()
                targets_pulled[starpool, stone_choice] += 1
            else:
                targets_pulled = event.targets_pulled

            new_event = EventState(orb_count, dry_streak, targets_pulled)

            states[StateStruct(
                sf_ify(new_event),
                sf_ify(new_session)
            )] += total_prob

    def push_outcome(event, probability):
        result = ResultState(event.orb_count, event.targets_pulled)
        outcomes[sf_ify(result)] += probability

    init_new_session(EventState(no_of_orbs, 0, 0*target_pool_counts),
                     Fraction(1))

    while states:
        print("\tno. of states:", len(states))

        (event, session), prob = states.popitem(-1)
        event = pd_ify(event)
        session = pd_ify(session)
        print('\torbs left:', event.orb_count)

        if not stone_chooser.should_continue(event.targets_pulled):
            print('chose to stop summoning')
            push_outcome(event, prob)
            continue

        if session.stone_counts.sum() == 0:
            print('completed summon session')
            init_new_session(event, prob)
            continue

        if event.orb_count < stone_cost(session.stone_counts.sum()):
            print('out of orbs')
            push_outcome(event, prob)
            continue

        stone_choice = stone_chooser.choose_stone(event.targets_pulled,
                                                  session.stone_counts,
                                                  ppcalc.pool() / pool_counts)
        if stone_choice is None:
            if session.stone_counts.sum() == summons_per_session:
                raise SummonChoiceError('cannot quit session without summoning'
                                        ' at least one Hero')
            print('quit summon session')
            init_new_session(event, prob)
        else:
            if session.stone_counts[stone_choice] == 0:
                raise SummonChoiceError('cannot summon colors that are not'
                                        ' present')
            print('chose to summon', stone_choice.name)
            branch_event(event, session, prob, stone_choice)

    return outcomes


def format_results(results):
    # TODO
    pass


def run():
    outcome_probs = get_outcomes(no_of_orbs=10,
                                 summon_behavior=ColorHunt)
    for state, prob in outcome_probs.items():
        print("{}: {:%}".format(state, float(prob)))
