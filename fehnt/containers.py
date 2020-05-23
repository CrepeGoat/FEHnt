"""
Contains all the custom container types for the package.
"""

from fractions import Fraction

import sortedcontainers as sc


class DefaultSortedDict(sc.SortedDict):
    """A sorted dictionary that pre-populates empty entries with zeros."""
    def __missing__(self, key):
        return Fraction()
