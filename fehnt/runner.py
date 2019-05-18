from .core import *

import static_frame as sf

def run():
    # (based on Heroes of Gallia summoning event)
    pool_counts = sf.Frame.from_records([
        (StarPools._5_STAR_FOCUS, Colors.RED, 1),
        (StarPools._5_STAR_FOCUS, Colors.BLUE, 1),
        (StarPools._5_STAR_FOCUS, Colors.GREEN, 1),
        #(StarPools._5_STAR_FOCUS, Colors.GRAY, 1),

        (StarPools._5_STAR, Colors.RED, 19),
        (StarPools._5_STAR, Colors.BLUE, 15),
        (StarPools._5_STAR, Colors.GREEN, 15),
        (StarPools._5_STAR, Colors.GRAY, 8),

        (StarPools._4_STAR, Colors.RED, 32),
        (StarPools._4_STAR, Colors.BLUE, 30),
        (StarPools._4_STAR, Colors.GREEN, 20),
        (StarPools._4_STAR, Colors.GRAY, 28),

        (StarPools._3_STAR, Colors.RED, 32),
        (StarPools._3_STAR, Colors.BLUE, 29),
        (StarPools._3_STAR, Colors.GREEN, 19),
        (StarPools._3_STAR, Colors.GRAY, 28),
    ], columns=['star', 'color', 'count']).set_index_hierarchy(
        ('star', 'color'), drop=True
    )['count']

    target_pool_counts = sf.Frame.from_records([
        (StarPools._5_STAR_FOCUS, Colors.BLUE, 1),
        (StarPools._5_STAR_FOCUS, Colors.GREEN, 1),
    ], columns=['star', 'color', 'count']).set_index_hierarchy(
        ('star', 'color'), drop=True
    )['count']

    outcome_probs = OutcomeCalculator(
        event_details=StandardEventDetails(pool_counts),
        summoner=ColorHuntSummoner(target_pool_counts),
    )(no_of_orbs=10)
    for state, prob in format_results(outcome_probs):
        print("{}: {:%}".format(state, float(prob)))
