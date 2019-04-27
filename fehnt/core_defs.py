import enum


@enum.unique
class Colors(enum.Enum):
    RED = 0
    BLUE = 1
    GREEN = 2
    GRAY = 3


@enum.unique
class StarRatings(enum.IntEnum):
    _5_STAR = 5
    _4_STAR = 4
    _3_STAR = 3


@enum.unique
class StarPools(enum.Enum):
    _5_STAR_FOCUS = 5.5
    _5_STAR = 5
    _4_STAR_FOCUS = 4.5
    _4_STAR = 4
    _3_STAR = 3


def stone_cost(stones_left):
    return {5: 5, 4: 4, 3: 4, 2: 4, 1: 3}[stones_left]


summons_per_session = 5
