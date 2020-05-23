from collections import namedtuple

import static_frame as sf

from fehnt.core_defs import Colors, stone_cost, SUMMONS_PER_SESSION

ColorTuple = namedtuple('EventState', [c.name for c in Colors])
EventState = namedtuple('EventState', 'orb_count dry_streak targets_pulled')


class SessionState(
    namedtuple('_', 'prob_level stone_summons stone_presences')
):
    def prob(self, event_details):
        """
        Calculate the probability of a session with the given stone
        limitations.
        """
        color_count_probs = event_details.color_count_probs(self.prob_level)
        return color_count_probs.loc[
            (
                color_count_probs.index >= tuple(self.stone_summons.values)
            ).all(axis=1)
            & (
                color_count_probs.index * tuple(1 - self.stone_presences.values)
                <= tuple(self.stone_summons.values)
            ).all(axis=1)
        ].sum()


class StateStruct(namedtuple('_', 'event session')):
    """
    Represents a unique state in summoning.

    This class also provides basic ordering among other class instances,
    s.t. if all elements are processed in order, like-states are aggregated
    first s.t. no identical states are re-processed multiple times.

    This is achieved by ordering states by the orb count *of its next post-
    processing state*.
    """

    def _obj_func(self):
        """Generate object representing a total ordering among states."""
        if self.session.stone_summons.sum() == SUMMONS_PER_SESSION:
            next_stone_cost = 1  # hack to make the comparison work
        else:
            next_stone_cost = stone_cost(self.session.stone_summons.sum())

        return (
            self.event.orb_count - next_stone_cost,
            self.session.stone_presences.sum(),
        )

    def __lt__(self, other):
        """Order states by summoning resources available."""
        return self._obj_func() < other._obj_func()


ResultState = namedtuple('ResultState', 'orb_count targets_pulled')


def nCkarray(*k_values):
    """Calculate nCk on a series of k values."""
    result = 1
    for i, j in enumerate((m for k in k_values for m in range(1, k+1)), 1):
        result = (result * i) // j
    return result


def multinomial_prob(counts, probs):
    """Calculate probability of a result from an multinomial distribution."""
    return nCkarray(*counts.values) * (probs ** counts).prod()


stone_combinations = [
    ColorTuple(i, j, k, SUMMONS_PER_SESSION-i-j-k)
    for i in range(SUMMONS_PER_SESSION+1)
    for j in range(SUMMONS_PER_SESSION+1-i)
    for k in range(SUMMONS_PER_SESSION+1-i-j)
]


def make_pool_counts(*pools):
    """Arrange pool counts into a static frame."""
    return sf.Frame.from_records(
        pools, columns=['star', 'color', 'count']
    ).set_index_hierarchy(
        ('star', 'color'), drop=True
    )['count']
