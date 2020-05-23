"""
Contains all the custom container types for the package.
"""

from fractions import Fraction

from frozendict import FrozenOrderedDict

import sortedcontainers as sc


class DefaultSortedDict(sc.SortedDict):
    """A sorted dictionary that pre-populates empty entries with zeros."""

    def __missing__(self, key):
        """Generate pre-populated values for missing keys."""
        return Fraction()


class HashableDict(FrozenOrderedDict):
    """A hashable dictionary."""

    def __hash__(self):
        """Hash the object's contents."""
        return hash(tuple(self.items()))


def reduce_along_axis(dict_, op, axis=-1, initial=0):
    """
    Reduce dimensionality of keys by aggregating an "axis" via a binary
    operation.
    """
    def strip_axis(key):
        """Remove axis from key."""
        return key[:axis] + key[axis+1 or len(key):]

    new_dict = {
        strip_axis(key): initial
        for key in dict_
    }

    for k, v in dict_:
        new_dict[strip_axis(k)] = op(new_dict[strip_axis(k)], dict_[k])

    if dict_.__class__ == dict:
        return new_dict

    return dict_.__class__(new_dict)


def expand_axes(dict1, dict2, op, dict_type=dict):
    """Compute the element-wise product between two mappings."""
    def combine_keys(key1, key2):
        """Combine component dict keys into a key for the new dict."""
        return (
            (key1 if isinstance(key1, tuple) else tuple(key1))
            + (key2 if isinstance(key2, tuple) else tuple(key2))
        )

    return dict_type(
        (combine_keys(k1, k2), op(v1, v2))
        for k1, v1 in dict1
        for k2, v2 in dict2
    )
