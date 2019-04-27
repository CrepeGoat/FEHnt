from .core_defs import *


class SummonChoiceError(RuntimeError):
    pass


class SummonChooser:
    def __init__(self, target_pool_counts):
        self.targets = target_pool_counts

    def should_continue(self, targets_pulled):
        # Default impementation. Should be overridden.
        return True

    def choose_stone(self, targets_pulled, stone_counts, unit_probs):
        # Default impementation. Should be overridden.
        for color, count in stone_counts.iteritems():
            if count:
                return color
        else:
            return None


class BlindFullSummon(SummonChooser):
    def should_continue(self, targets_pulled):
        # TODO make more sophisticated stone-choosing functions
        return self.targets.sub(targets_pulled, fill_value=0).any()

    def choose_stone(self, targets_pulled, stone_counts, unit_probs):
        # TODO make more sophisticated stone-choosing functions
        return super().choose_stone(targets_pulled, stone_counts, unit_probs)


class ColorHunt(SummonChooser):
    def should_continue(self, targets_pulled):
        # TODO make more sophisticated stone-choosing functions
        return self.targets.sub(targets_pulled, fill_value=0).any()

    def choose_stone(self, targets_pulled, stone_counts, unit_probs):
        # TODO make more sophisticated stone-choosing functions
        targets_left = self.targets.sub(targets_pulled, fill_value=0)
        expt_yield = (targets_left
                      .mul(unit_probs, fill_value=0)
                      .groupby(level='color', sort=False)
                      .sum())
        available_yield = expt_yield * stone_counts.astype(bool)
        optimal_choice = available_yield.idxmax()

        if available_yield[optimal_choice] == 0:
            if stone_counts.sum() < summons_per_session:
                return None
            else:
                # TODO choose color w/ lowest chance of resetting dry streak
                return super().choose_stone(targets_pulled, stone_counts,
                                            unit_probs)
        else:
            return optimal_choice
