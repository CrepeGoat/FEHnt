from .core_defs import *
from .core_utils import *
from .pd_sf_convert import *
from .event_behaviors import *
from .summoner_behaviors import *

from collections import defaultdict
from fractions import Fraction

import pandas as pd
import sortedcontainers as sc


class DefaultSortedDict(sc.SortedDict):
    def __missing__(self, key):
        return Fraction()


class OutcomeCalculator:
    def __init__(self, event_details, summoner):
        self.event_details = event_details
        self.summoner = summoner

    def __len__(self):
        return len(self.states)

    def __next__(self):
        return self.states.popitem(-1)

    def init_new_session(self, event, probability):
        prob_tier = event.dry_streak // summons_per_session
        color_probs = self.event_details.colorpool_probs(prob_tier)

        for stones, stones_prob in stone_combinations(color_probs):
            self.states[StateStruct(
                sf_ify(event),
                sf_ify(SessionState(prob_tier, stones))
            )] += probability * stones_prob

    def branch_event(self, event, session, prob, stone_choice):
        new_session = session._replace(
            stone_counts=session.stone_counts.sub(
                pd.Series([1], index=[stone_choice]), fill_value=0
            )
        )
        orb_count = event.orb_count - stone_cost(session.stone_counts.sum())

        choice_starpool_probs = (self.event_details
                                 .pool_probs(session.prob_level)
                                 .xs(stone_choice, level='color'))
        choice_starpool_probs /= choice_starpool_probs.sum()

        for starpool, subprob in choice_starpool_probs.iteritems():
            total_prob = prob * subprob

            if starpool in (StarPools._5_STAR_FOCUS, StarPools._5_STAR):
                dry_streak = 0
            else:
                dry_streak = event.dry_streak + 1

            if (starpool, stone_choice) not in self.summoner.targets.index:
                pulls = ((event.targets_pulled, 1),)
            else:
                targets_pulled_success = event.targets_pulled.copy()
                targets_pulled_success[starpool, stone_choice] += 1
                prob_success = Fraction(
                    int(self.summoner.targets[starpool, stone_choice]),
                    int(self.event_details.pool_counts[starpool, stone_choice])
                )

                pulls = (
                    (targets_pulled_success, prob_success),
                    (event.targets_pulled, 1-prob_success)
                )

            for targets_pulled, subsubprob in pulls:
                new_event = EventState(orb_count, dry_streak, targets_pulled)

                self.states[StateStruct(
                    sf_ify(new_event),
                    sf_ify(new_session)
                )] += total_prob * subsubprob

    def push_outcome(self, event, probability):
        result = ResultState(event.orb_count, event.targets_pulled)
        self.outcomes[sf_ify(result)] += probability

    def __call__(self, no_of_orbs):
        self.states = DefaultSortedDict()
        self.outcomes = defaultdict(Fraction, [])

        self.init_new_session(
            EventState(no_of_orbs, 0, 0*self.summoner.targets), Fraction(1)
        )

        while self:
            print("  no. of states:", len(self))

            (event, session), prob = next(self)
            event = pd_ify(event)
            session = pd_ify(session)
            print('  orbs left:', event.orb_count)

            if not self.summoner.should_continue(event.targets_pulled):
                print('chose to stop summoning')
                self.push_outcome(event, prob)
                continue

            if session.stone_counts.sum() == 0:
                print('completed summon session')
                self.init_new_session(event, prob)
                continue

            if event.orb_count < stone_cost(session.stone_counts.sum()):
                print('out of orbs')
                self.push_outcome(event, prob)
                continue

            stone_choice = self.summoner.choose_stone(
                event.targets_pulled,
                session.stone_counts,
                self.event_details.pool_probs() / self.event_details.pool_counts
            )
            if stone_choice is None:
                if session.stone_counts.sum() == summons_per_session:
                    raise SummonChoiceError('cannot quit session without summoning'
                                            ' at least one Hero')
                print('quit summon session')
                self.init_new_session(event, prob)
            else:
                if session.stone_counts[stone_choice] == 0:
                    raise SummonChoiceError('cannot summon colors that are not'
                                            ' present')
                print('chose to summon', stone_choice.name)
                self.branch_event(event, session, prob, stone_choice)

        return self.outcomes


def format_results(results):
    # TODO
    yield_probs = defaultdict(Fraction, [])
    for state, prob in results.items():
        yield_probs[state.targets_pulled] += prob

    return [(k, float(v)) for k, v in yield_probs.items()]
