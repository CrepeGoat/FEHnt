from .core_defs import *
from .core_utils import *
from .event_behaviors import *
from .summoner_behaviors import *

from collections import defaultdict
from fractions import Fraction

import static_frame as sf
import sortedcontainers as sc


class DefaultSortedDict(sc.SortedDict):
    def __missing__(self, key):
        return Fraction()


def get_outcomes(event_details, summoner, no_of_orbs):
    states = DefaultSortedDict()
    outcomes = defaultdict(Fraction, [])

    def init_new_session(event, probability):
        prob_tier = event.dry_streak // summons_per_session
        color_probs = event_details.colorpool_probs(prob_tier)

        for stones, stones_prob in stone_combinations(color_probs):
            states[StateStruct(
                event, SessionState(prob_tier, stones)
            )] += probability * stones_prob

    def branch_event(event, session, prob, stone_choice):
        stone_count_choice = (sf.Series([1], index=[stone_choice])
                              .reindex(session.stone_counts.index,
                                       fill_value=0))
        new_session = session._replace(
            stone_counts=session.stone_counts - stone_count_choice
        )
        orb_count = event.orb_count - stone_cost(session.stone_counts.sum())

        choice_starpool_probs = (event_details
                                 .pool_probs(session.prob_level)
                                 [sf.HLoc[:, stone_choice]]
                                 .reindex_drop_level())

        choice_starpool_probs = (choice_starpool_probs
                                 / choice_starpool_probs.sum())

        for starpool, subprob in choice_starpool_probs.iter_element_items():
            total_prob = prob * subprob

            if starpool in (StarPools._5_STAR_FOCUS, StarPools._5_STAR):
                dry_streak = 0
            else:
                dry_streak = event.dry_streak + 1

            if (starpool, stone_choice) not in summoner.targets.index:
                pulls = ((event.targets_pulled, 1),)
            else:
                targets_pulled_success = event.targets_pulled + sf.Series(
                    [1], index=sf.IndexHierarchy.from_labels([
                        (starpool, stone_choice)
                    ])
                ).reindex(event.targets_pulled.index, fill_value=0)

                prob_success = Fraction(
                    int(summoner.targets[starpool, stone_choice]),
                    int(event_details.pool_counts[starpool, stone_choice])
                )

                pulls = (
                    (targets_pulled_success, prob_success),
                    (event.targets_pulled, 1-prob_success)
                )

            for targets_pulled, subsubprob in pulls:
                new_event = EventState(orb_count, dry_streak, targets_pulled)

                states[StateStruct(new_event, new_session)] += total_prob * subsubprob

    def push_outcome(event, probability):
        result = ResultState(event.orb_count, event.targets_pulled)
        outcomes[result] += probability

    init_new_session(EventState(no_of_orbs, 0, 0*summoner.targets),
                     Fraction(1))

    while states:
        print("\tno. of states:", len(states))

        (event, session), prob = states.popitem(-1)
        event = event
        session = session
        print('\torbs left:', event.orb_count)

        if not summoner.should_continue(event.targets_pulled):
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

        stone_choice = summoner.choose_stone(
            event.targets_pulled,
            session.stone_counts,
            event_details.pool_probs() / event_details.pool_counts
        )
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
    yield_probs = defaultdict(Fraction, [])
    for state, prob in results.items():
        yield_probs[state.targets_pulled] += prob

    return [(k, float(v)) for k, v in yield_probs.items()]
