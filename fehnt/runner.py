from .core import *


def run():
    """Run calculations."""
    # (based on Heroes of Gallia summoning event)
    pool_counts = make_pool_counts(
        (StarPools.x5_STAR_FOCUS, Colors.RED, 1),
        (StarPools.x5_STAR_FOCUS, Colors.BLUE, 1),
        (StarPools.x5_STAR_FOCUS, Colors.GREEN, 1),
        (StarPools.x5_STAR_FOCUS, Colors.GRAY, 1),

        (StarPools.x5_STAR, Colors.RED, 19),
        (StarPools.x5_STAR, Colors.BLUE, 15),
        (StarPools.x5_STAR, Colors.GREEN, 15),
        (StarPools.x5_STAR, Colors.GRAY, 8),

        (StarPools.x4_STAR, Colors.RED, 32),
        (StarPools.x4_STAR, Colors.BLUE, 30),
        (StarPools.x4_STAR, Colors.GREEN, 20),
        (StarPools.x4_STAR, Colors.GRAY, 28),

        (StarPools.x3_STAR, Colors.RED, 32),
        (StarPools.x3_STAR, Colors.BLUE, 29),
        (StarPools.x3_STAR, Colors.GREEN, 19),
        (StarPools.x3_STAR, Colors.GRAY, 28),
    )

    target_pool_counts = make_pool_counts(
        (StarPools.x5_STAR_FOCUS, Colors.RED, 1),
    )

    outcomes = OutcomeCalculator(
        event_details=EventDetails.make_standard(pool_counts),
        summoner=ColorHuntSummoner(target_pool_counts),
        callback=lambda *args: None,
    )
    for orbs_spent, outcome_probs in outcomes:
        print(f'orbs: {orbs_spent}')
        if orbs_spent == 10:
            break
    for state, prob in condense_results(outcome_probs):
        print("{}: {:%}".format(state, float(prob)))
