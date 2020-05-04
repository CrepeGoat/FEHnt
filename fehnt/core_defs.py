import enum


@enum.unique
class Colors(enum.Enum):
    """Unit colors."""

    RED = 0
    BLUE = 1
    GREEN = 2
    GRAY = 3

    def __lt__(self, other):
        """Order color objects."""
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.value < other.value


@enum.unique
class StarRatings(enum.IntEnum):
    """Unit star ratings."""

    _5_STAR = 5
    _4_STAR = 4
    _3_STAR = 3


@enum.unique
class StarPools(enum.Enum):
    """Unit star rating summon pools."""

    _5_STAR_FOCUS = 5.5
    _5_STAR = 5
    _4_STAR_FOCUS = 4.5
    _4_STAR = 4
    _3_STAR = 3

    def __lt__(self, other):
        """Order star pool objects."""
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.value < other.value


_STONE_COSTS = (None, 3, 4, 4, 4, 5)


def stone_cost(stones_left):
    """Get orb cost of next summoning in current session."""
    return _STONE_COSTS[int(stones_left)]  # TODO fix implicit cast to float


SUMMONS_PER_SESSION = 5
