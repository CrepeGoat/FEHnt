import enum


@enum.unique
class Colors(enum.Enum):
    RED = 0
    BLUE = 1
    GREEN = 2
    GRAY = 3

    def __lt__(self, other):
        return self.value < other.value


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

    def __lt__(self, other):
        return self.value < other.value


stone_costs = (None, 3, 4, 4, 4, 5)


def stone_cost(stones_left):
    return stone_costs[int(stones_left)]  # TODO fix implicit cast to float


summons_per_session = 5
