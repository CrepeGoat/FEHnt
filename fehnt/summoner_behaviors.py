import numpy as np

from .core_defs import summons_per_session


class SummonChoiceError(RuntimeError):
    pass


class SummonerBehavior:
    def __init__(self, target_pool_counts):
        self.targets = target_pool_counts

    def _targets_left(self, targets_pulled):
        full_targets_pulled = targets_pulled.reindex(self.targets.index,
                                                     fill_value=0)
        return self.targets - full_targets_pulled

    def should_continue(self, targets_pulled):
        # Default impementation. Should be overridden.
        return True

    def choose_stone(self, targets_pulled, stone_counts, unit_probs):
        # Default impementation. Should be overridden.
        return next((color for color, count in stone_counts.iter_element_items()
                     if count), None)


class BlindFullSummoner(SummonerBehavior):
    def should_continue(self, targets_pulled):
        # TODO make more sophisticated stone-choosing functions
        return self._targets_left(targets_pulled).any()

    def choose_stone(self, targets_pulled, stone_counts, unit_probs):
        # TODO make more sophisticated stone-choosing functions
        return super().choose_stone(targets_pulled, stone_counts, unit_probs)


class ColorHuntSummoner(SummonerBehavior):
    def should_continue(self, targets_pulled):
        # TODO make more sophisticated stone-choosing functions
        return self._targets_left(targets_pulled).any()

    def choose_stone(self, targets_pulled, stone_counts, unit_probs):
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
            if stone_counts.sum() < summons_per_session:
                return None
            else:
                # TODO choose color w/ lowest chance of resetting dry streak
                return super().choose_stone(targets_pulled, stone_counts,
                                            unit_probs)
        else:
            return optimal_choice
