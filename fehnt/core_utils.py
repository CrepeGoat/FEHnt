from collections import namedtuple

import static_frame as sf

from fehnt.core_defs import Colors, SUMMONS_PER_SESSION


EventState = namedtuple('EventState', 'orb_count dry_streak targets_pulled')
SessionState = namedtuple('SessionState', 'prob_level stone_counts')


class StateStruct(namedtuple('_', 'event session')):
    """
    Represents a unique state in summoning.

    This class also provides basic ordering among other class instances,
    s.t. if all elements are processed in order, any/all identical states will
    be aggregated before either is processed.

    This is achieved under two rules:
    - a high-orb state yields a low-orb state after processing
      -> high-orb states are "greater"
    - a low-stone session requires fewer orbs to process, and thus processes
      down to higher-orb states than high-stone states
      -> low-stone states are "greater"
    """

    def _obj_func(self):
        """Generate object representing a total ordering among states."""
        return (self.event.orb_count, -self.session.stone_counts.sum())

    def __lt__(self, other):
        """Order states by summoning resources available."""
        return self._obj_func() < other._obj_func()


ResultState = namedtuple('ResultState', 'orb_count targets_pulled')


def nCkarray(k_array):
    """Calculate nCk on a series of k values."""
    result = 1
    for i, j in enumerate((m for k in k_array for m in range(1, k+1)), 1):
        result = (result * i) // j
    return result


def multinomial_prob(counts, probs):
    """Calculate probability of a result from an multinomial distribution."""
    return nCkarray(counts.values) * (probs ** counts).prod()


# @lru_cache(maxsize=None)
def stone_combinations(color_probs):
    """Iterate through all possible stone combinations in a given session."""
    return ((s, multinomial_prob(s, color_probs))
            for s in stone_combinations.cache.iter_series(axis=1))


stone_combinations.cache = sf.Frame.from_records([
    (i, j, k, SUMMONS_PER_SESSION-i-j-k)
    for i in range(SUMMONS_PER_SESSION+1)
    for j in range(SUMMONS_PER_SESSION+1-i)
    for k in range(SUMMONS_PER_SESSION+1-i-j)
], columns=[c for c in Colors])


def make_pool_counts(pools):
    """Arrange pool counts into a static frame."""
    return sf.Frame.from_records(
        pools, columns=['star', 'color', 'count']
    ).set_index_hierarchy(
        ('star', 'color'), drop=True
    )['count']
