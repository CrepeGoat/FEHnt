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

        # Lazily instantiated
        self.states = None
        self.outcomes = None

    def process_stone_choice_sequence(
        self, event, session, prob, stone_choice_sequence
    ):
        """
        Calculate event states following a single summon characterized by stone
        choice sequence.
        """
        assert session.stone_presences.any()

        for stone_choice in stone_choice_sequence:
            if session.stone_presences[stone_choice]:
                break
        else:
            if session.stone_summons.sum() == 0:
                raise SummonChoiceError(
                    'cannot quit session without summoning at least one Hero'
                )
            self.callback('left summoning session')
            self.init_new_session(event, prob)
            return

        self.callback('chose to summon', stone_choice.name)

        if session.stone_presences.sum() > 1:
            alt_session = session._replace(stone_presences=(
                session.stone_presences.assign[stone_choice](False)
            ))
            alt_subprob = (
                alt_session.prob(self.event_details)
                / session.prob(self.event_details)
            )
            self.states[StateStruct(event, alt_session)] += prob * alt_subprob

            prob *= (1-alt_subprob)

        new_session = session._replace(
            stone_summons=session.stone_summons.assign[stone_choice](
                session.stone_summons[stone_choice] + 1
            )
        )
        self.branch_event(event, new_session, prob, stone_choice)

    def init_new_session(self, event, prob):
        """Add new summoning session after an existing session finishes."""
        if not self.summoner.should_start_new_session(event.targets_pulled):
            self.callback('quit summoning event')
            self.push_outcome(event, prob)
            return

        self.states[StateStruct(event, SessionState(
            prob_tier=event.dry_streak // SUMMONS_PER_SESSION,
            stone_summons=sf.Series(0, index=tuple(Colors)),
            stone_presences=sf.Series(True, index=tuple(Colors)),
        ))] += prob

    def branch_event(self, event, session, prob, stone_choice):
        """Split session into all potential following sub-sessions."""
        orbs_spent = event.orbs_spent + stone_cost(session.stone_summons.sum()-1)

        choice_starpool_probs = (self.event_details
                                 .pool_probs(session.prob_tier)
                                 [sf.HLoc[:, stone_choice]]
                                 .reindex_drop_level(-1))

        choice_starpool_probs = (choice_starpool_probs
                                 / choice_starpool_probs.sum())

        for starpool, subprob in choice_starpool_probs.iter_element_items():
            total_prob = prob * subprob

            if starpool.star_rating == StarRatings.x5_STAR:
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
                new_event = EventState(orbs_spent, dry_streak, targets_pulled)

                self.states[StateStruct(new_event, session)] += (
                    total_prob * subsubprob
                )

    def push_outcome(self, event, prob):
        """Add a given probabilistic outcome to the recorded results."""
        result = ResultState(event.orbs_spent, event.targets_pulled)
        self.outcomes[result] += prob

    def __call__(self, no_of_orbs):
        """Calculate the summoning probabilities."""
        self.states = DefaultSortedDict()
        self.outcomes = defaultdict(Fraction, [])

        self.init_new_session(
            EventState(0, 0, 0*self.summoner.targets), Fraction(1)
        )

        def iter_states():
            """Iterate state nodes."""
            while self.states:
                yield self.states.popitem(-1)

        for i, ((event, session), prob) in enumerate(iter_states()):
            self.callback("  state no.:", i)
            self.callback("  no. of states in queue:", len(self.states))
            self.callback('  orbs spent:', event.orbs_spent)

            if session.stone_summons.sum() == SUMMONS_PER_SESSION:
                self.callback('completed summoning session')
                self.init_new_session(event, prob)
                continue

            if (
                event.orbs_spent + stone_cost(session.stone_summons.sum())
                > no_of_orbs
            ):
                self.callback('out of orbs')
                self.push_outcome(event, prob)
                continue

            stone_choice_sequence = self.summoner.stone_choice_sequence(
                event.targets_pulled,
                session.stone_summons.sum(),
                unit_probs=self.event_details.pool_probs(
                    prob_tier=session.prob_tier
                ) / self.event_details.pool_counts,
            )
            self.process_stone_choice_sequence(
                event, session, prob, stone_choice_sequence
            )

        return self.outcomes


def condense_results(results):
    """Reduces results to probabilities of obtaining a given set of units."""
    # TODO
    yield_probs = defaultdict(Fraction, [])
    for state, prob in results.items():
        yield_probs[state.targets_pulled] += prob

    return list(yield_probs.items())
