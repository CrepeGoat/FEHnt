import numpy as np

from .core_defs import Colors, SUMMONS_PER_SESSION


class SummonChoiceError(RuntimeError):
    """Error raised when invalid summon choices are made."""
    pass


class SummonerBehavior:
    """Base cass representing summoner behavior in summoning sessions."""

    def __init__(self, target_pool_counts):
        """Construct an instance."""
        self.targets = target_pool_counts

    def _targets_left(self, targets_pulled):
        """Count target units successfully summoned."""
        full_targets_pulled = targets_pulled.reindex(self.targets.index,
                                                     fill_value=0)
        return self.targets - full_targets_pulled

    def should_start_new_session(self, targets_pulled):
        """
        Check whether a new session should be started.

        Default impementation. Should be overridden.
        """
        return True

    def stone_choice_sequence(self, targets_pulled, stones_count, unit_probs):
        """
        Generate characteristic stone color choice sequence.

        A summoner's choices in a given session state are characterized by an
        ordered sequence of preferred stone color choices, stone color presence
        allowing.

        E.g., for the choice sequence [BLUE, GREEN, GRAY]:
        - if a BLUE stone is present, the summoner will choose a BLUE stone
          regardless of the other stones available.
        - if no BLUE stones are present, but a GREEN *is*, the summoner will
          choose a GREEN stone.
        - if no BLUE/GREEN stones are present, but a GRAY *is*, the summoner
          will choose a GRAY stone.
        - if no BLUE/GREEN/GRAY stones are present (i.e., all are RED), then
          the summoner will stop the summoning session short.

        ***
        This assumes that stone preferences are independent of stone presence.
        E.g., whether or not BLUE is my favorite does *not* depend on whether
        a GREEN stone is present.
        ***
        """
        return tuple(Colors)


class BlindFullSummoner(SummonerBehavior):
    """Summoner behavior for choosing all stones."""

    def should_start_new_session(self, targets_pulled):
        """Check whether a new session should be started."""
        # TODO make more sophisticated stone-choosing functions
        return self._targets_left(targets_pulled).any()


class ColorHuntSummoner(SummonerBehavior):
    """Summoner behavior for choosing stones of target colors only."""

    def should_start_new_session(self, targets_pulled):
        """Check whether a new session should be started."""
        return self._targets_left(targets_pulled).any()

    def stone_choice_sequence(self, targets_pulled, stones_count, unit_probs):
        """Generate characteristic stone color choice sequence."""
        targets_left = self.targets - targets_pulled.reindex(
            self.targets.index, fill_value=0
        )
        expt_yield = ((unit_probs * targets_left.reindex(unit_probs.index,
                                                         fill_value=0))
                      .iter_group_index(1)
                      .apply(np.sum))
        expt_yield = expt_yield.loc[expt_yield.values > 0]

        optimal_choice_sequence = tuple(expt_yield.index[np.argsort(
            expt_yield.values, kind='stable'
        )[::-1]])
        if stones_count == SUMMONS_PER_SESSION:
            optimal_choice_sequence = optimal_choice_sequence + tuple(
                i for i in Colors if i not in optimal_choice_sequence
            )
            assert len(optimal_choice_sequence) == len(Colors)

        return optimal_choice_sequence
