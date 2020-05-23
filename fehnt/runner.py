import static_frame as sf

from .core import *


def run():
    """Run calculations."""
    # (based on Heroes of Gallia summoning event)
    pool_counts = make_pool_counts(
        (StarPools._5_STAR_FOCUS, Colors.RED, 1),
        (StarPools._5_STAR_FOCUS, Colors.BLUE, 1),
        (StarPools._5_STAR_FOCUS, Colors.GRAY, 1),

        (StarPools._5_STAR, Colors.RED, 57),
        (StarPools._5_STAR, Colors.BLUE, 38),
        (StarPools._5_STAR, Colors.GREEN, 34),
        (StarPools._5_STAR, Colors.GRAY, 26),

        (StarPools._4_STAR, Colors.RED, 33),
        (StarPools._4_STAR, Colors.BLUE, 34),
        (StarPools._4_STAR, Colors.GREEN, 24),
        (StarPools._4_STAR, Colors.GRAY, 35),

        (StarPools._3_STAR, Colors.RED, 33),
        (StarPools._3_STAR, Colors.BLUE, 33),
        (StarPools._3_STAR, Colors.GREEN, 24),
        (StarPools._3_STAR, Colors.GRAY, 35),
    )

    target_pool_counts = make_pool_counts(
        (StarPools._5_STAR_FOCUS, Colors.RED, 1),
    )

    outcome_probs = OutcomeCalculator(
        event_details=StandardEventDetails(pool_counts),
        summoner=ColorHuntSummoner(target_pool_counts),
    )(no_of_orbs=84)
    for state, prob in condense_results(outcome_probs):
        print("{}: {:%}".format(state, float(prob)))
