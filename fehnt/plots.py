"""
Reference: matplotlib.org/3.2.1/gallery/lines_bars_and_markers/
           horizontal_barchart_distribution.html
"""

from itertools import takewhile

import numpy as np
import matplotlib.pyplot as plt


def count_pulls(outcomes):
    """Aggregate probabilities of equal-quantity outcomes."""
    results = []
    for state, prob in outcomes.items():
        pull_count = state.targets_pulled.sum()
        results.extend(0 for _ in range(pull_count - len(results) + 1))

        results[pull_count] += prob

    return [float(i) for i in results]


def survey(outcomes_iter, max_orbs=100):
    """
    Parameters
    ----------
    results : dict
        A mapping from question labels to a list of answers per category.
        It is assumed all lists contain the same number of entries and that
        it matches the length of *category_names*.
    category_names : list of str
        The category labels.
    """
    results = {
        orbs: count_pulls(outcomes)
        for (orbs, outcomes) in takewhile(
            lambda x: x[0] <= max_orbs,
            outcomes_iter,
        )
    }

    bin_count = max(len(pull_counts) for pull_counts in results.values())
    for pull_counts in results.values():
        pull_counts.extend(0 for _ in range(bin_count - len(pull_counts)))

    labels = list(results.keys())
    data = np.array(list(results.values()))
    data_cum = data.cumsum(axis=1)
    category_colors = plt.get_cmap('RdYlGn')(
        np.linspace(0.15, 0.85, data.shape[1]))

    print('time to make the plot')
    fig, ax = plt.subplots(figsize=(9.2, 5))
    ax.invert_yaxis()
    ax.xaxis.set_visible(False)
    ax.set_xlim(0, np.sum(data, axis=1).max())

    for i, color in enumerate(category_colors):
        widths = data[:, i]
        starts = data_cum[:, i] - widths
        ax.barh(labels, widths, left=starts, height=0.5,
                label=str(i), color=color)
        xcenters = starts + widths / 2

        r, g, b, _ = color
        text_color = 'white' if r * g * b < 0.5 else 'darkgrey'
        for y, (x, c) in enumerate(zip(xcenters, widths)):
            ax.text(x, y, str(int(c)), ha='center', va='center',
                    color=text_color)
    ax.legend(ncol=bin_count, bbox_to_anchor=(0, 1),
              loc='lower left', fontsize='small')

    print('plot made!')
    return fig, ax


if __name__ == '__main__':
    from fehnt.core import *

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

    outcomes_iter = OutcomeCalculator(
        event_details=EventDetails.make_standard(pool_counts),
        summoner=ColorHuntSummoner(target_pool_counts),
    )

    survey(outcomes_iter, max_orbs=20)
    plt.show()
