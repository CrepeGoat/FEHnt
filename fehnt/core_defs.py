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

    x5_STAR = 5
    x4_STAR = 4
    x3_STAR = 3


@enum.unique
class StarPools(enum.Enum):
    """Unit star rating summon pools."""

    x5_STAR_FOCUS = (5, True)
    x5_STAR = (5, False)
    x4_STAR_FOCUS = (4, True)
    x4_STAR = (4, False)
    x3_STAR = (3, False)

    def __lt__(self, other):
        """Order star pool objects."""
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.value < other.value

    @property
    def star_rating(self):
        return StarRatings(self.value[0])

    @property
    def is_focus(self):
        return self.value[1]


_STONE_COSTS = (5, 4, 4, 4, 3)


def stone_cost(stones_summoned):
    """Get orb cost of next summoning in current session."""
    return _STONE_COSTS[int(stones_summoned)]  # TODO fix implicit cast to float


SUMMONS_PER_SESSION = 5
