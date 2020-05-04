from collections import defaultdict
from fractions import Fraction

import sortedcontainers as sc
import static_frame as sf

from .core_defs import *
from .core_utils import *
from .event_behaviors import *
from .summoner_behaviors import *


class DefaultSortedDict(sc.SortedDict):
    """A sorted dictionary that pre-populates empty entries with zeros."""
    def __missing__(self, key):
        return Fraction()


class OutcomeCalculator:
    """
    An object that calculates summoning probabilities.

    The core object of FEHnt.
    """

    def __init__(self, event_details, summoner, callback=print):
        """Construct an instance."""
        self.event_details = event_details
        self.summoner = summoner
        self.callback = callback

    def __iter__(self):
        """Iterate summoning states."""
        return self

    def __next__(self):
        """Get next summoning state."""
        if len(self.states) == 0:
            raise StopIteration
        return self.states.popitem(-1)

    def init_new_session(self, event, probability):
        """Add new summoning session after an existing session finishes."""
        prob_tier = event.dry_streak // SUMMONS_PER_SESSION
        color_probs = self.event_details.colorpool_probs(prob_tier)

        for stones, stones_prob in stone_combinations(color_probs):
            self.states[StateStruct(
                event, SessionState(prob_tier, stones)
            )] += probability * stones_prob

    def branch_event(self, event, session, prob, stone_choice):
        """Split session into all potential following sub-sessions."""
        stone_count_choice = (sf.Series([1], index=[stone_choice])
                              .reindex(session.stone_counts.index,
                                       fill_value=0))
        new_session = session._replace(
            stone_counts=session.stone_counts - stone_count_choice
        )
        orb_count = event.orb_count - stone_cost(session.stone_counts.sum())

        choice_starpool_probs = (self.event_details
                                 .pool_probs(session.prob_level)
                                 [sf.HLoc[:, stone_choice]]
                                 .reindex_drop_level(-1))

        choice_starpool_probs = (choice_starpool_probs
                                 / choice_starpool_probs.sum())

        for starpool, subprob in choice_starpool_probs.iter_element_items():
            total_prob = prob * subprob

            if starpool in (StarPools._5_STAR_FOCUS, StarPools._5_STAR):
                dry_streak = 0
            else:
                dry_streak = event.dry_streak + 1

            if (starpool, stone_choice) not in self.summoner.targets.index:
                pulls = ((event.targets_pulled, 1),)
            else:
                targets_pulled_success = event.targets_pulled + sf.Series(
                    [1], index=sf.IndexHierarchy.from_labels([
                        (starpool, stone_choice)
                    ])
                ).reindex(event.targets_pulled.index, fill_value=0)

                prob_success = Fraction(
                    int(self.summoner.targets[starpool, stone_choice]),
                    int(self.event_details.pool_counts[starpool, stone_choice])
                )

                pulls = ((targets_pulled_success, prob_success),
                         (event.targets_pulled, 1-prob_success))

            for targets_pulled, subsubprob in pulls:
                new_event = EventState(orb_count, dry_streak, targets_pulled)

                self.states[StateStruct(new_event, new_session)] += (
                    total_prob * subsubprob
                )

    def push_outcome(self, event, probability):
        """Add a given probabilistic outcome to the recorded results."""
        result = ResultState(event.orb_count, event.targets_pulled)
        self.outcomes[result] += probability

    def __call__(self, no_of_orbs):
        """Calculate the summoning probabilities."""
        self.states = DefaultSortedDict()
        self.outcomes = defaultdict(Fraction, [])

        self.init_new_session(
            EventState(no_of_orbs, 0, 0*self.summoner.targets), Fraction(1)
        )

        for i, ((event, session), prob) in enumerate(self):
            self.callback("  state no.:", i)
            self.callback("  no. of states in queue:", len(self.states))
            self.callback('  orbs left:', event.orb_count)

            if not self.summoner.should_start_new_session(event.targets_pulled):
                self.callback('quit summoning event')
                self.push_outcome(event, prob)
                continue

            if session.stone_counts.sum() == 0:
                self.callback('completed summoning session')
                self.init_new_session(event, prob)
                continue

            if event.orb_count < stone_cost(session.stone_counts.sum()):
                self.callback('out of orbs')
                self.push_outcome(event, prob)
                continue

            stone_choice = self.summoner.choose_stone(
                event.targets_pulled,
                session.stone_counts,
                self.event_details.pool_probs() / self.event_details.pool_counts
            )
            if stone_choice is None:
                if session.stone_counts.sum() == SUMMONS_PER_SESSION:
                    raise SummonChoiceError('cannot quit session without summoning'
                                            ' at least one Hero')
                self.callback('left summoning session')
                self.init_new_session(event, prob)
            else:
                if session.stone_counts[stone_choice] == 0:
                    raise SummonChoiceError('cannot summon colors that are not'
                                            ' present')
                self.callback('chose to summon', stone_choice.name)
                self.branch_event(event, session, prob, stone_choice)

        return self.outcomes


def condense_results(results):
    """Reduces results to probabilities of obtaining a given set of units."""
    # TODO
    yield_probs = defaultdict(Fraction, [])
    for state, prob in results.items():
        yield_probs[state.targets_pulled] += prob

    return list(yield_probs.items())
