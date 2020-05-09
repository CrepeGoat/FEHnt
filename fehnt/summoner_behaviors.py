import numpy as np

from .core_defs import SUMMONS_PER_SESSION


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

    def choose_stone(self, targets_pulled, stone_counts, unit_probs):
        """
        Choose an available stone in the given session.

        Default impementation. Should be overridden.
        """
        return next((color for color, count in stone_counts.iter_element_items()
                     if count), None)


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
        # TODO make more sophisticated stone-choosing functions
        return self._targets_left(targets_pulled).any()

    def choose_stone(self, targets_pulled, stone_counts, unit_probs):
        """Choose an available stone in the given session."""
        # TODO make more sophisticated stone-choosing functions
        targets_left = self.targets - targets_pulled.reindex(
            self.targets.index, fill_value=0
        )
        expt_yield = ((unit_probs * targets_left.reindex(unit_probs.index,
                                                         fill_value=0))
                      .iter_group_index(1)
                      .apply(np.sum))
        available_yield = expt_yield * stone_counts.astype(bool)
        optimal_choice = available_yield.index[available_yield.values.argmax()]

        if available_yield[optimal_choice] == 0:
            if stone_counts.sum() < SUMMONS_PER_SESSION:
                return None
            # TODO choose color w/ lowest chance of resetting dry streak
            return super().choose_stone(targets_pulled, stone_counts,
                                        unit_probs)

        return optimal_choice
