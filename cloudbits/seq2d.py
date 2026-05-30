"""
2D generalised Fibonacci grid utilities.

Seed block occupies (0,0), (-1,0), (0,-1), (-1,-1).
Positive direction: f(i,j) = f(i-1,j) + f(i-2,j)
Negative direction: f(i,j) = f(i+2,j) - f(i+1,j)
Same recurrence runs independently along each axis.

CoeffTuple / make_coeff_grid provide seed-independent (universal) arithmetic
for the Cloudbits validation engine.  make_2dseq is retained for any callers
that need a numeric grid.
"""


class CoeffTuple:
    """
    Linear combination of the four Lens seed values for one grid cell.

    Every cell's value is always  ca*a + cb*b + cc*c + cd*d  regardless of
    the specific seed chosen.  CoeffTuple stores (ca, cb, cc, cd).
    """

    __slots__ = ('v',)

    def __init__(self, components):
        self.v = tuple(components)

    def __add__(self, other):
        return CoeffTuple(x + y for x, y in zip(self.v, other.v))

    def __sub__(self, other):
        return CoeffTuple(x - y for x, y in zip(self.v, other.v))

    def __eq__(self, other):
        if isinstance(other, CoeffTuple):
            return self.v == other.v
        return NotImplemented

    def __repr__(self):
        return f"CoeffTuple{self.v}"


def make_coeff_grid(half: int = 15) -> dict:
    """
    Build a coefficient grid for a 2D Fibonacci sequence centred at (0,0).

    Each cell stores a CoeffTuple (ca, cb, cc, cd).  Lens cells are seeded
    with unit vectors:

        (1,0,0,0) at ( 0, 0)     (0,1,0,0) at (-1, 0)
        (0,0,1,0) at ( 0,-1)     (0,0,0,1) at (-1,-1)

    Returns dict mapping (i, j) → CoeffTuple, covering i,j in [-(half+1), half].
    """
    f = {}
    f[( 0,  0)] = CoeffTuple((1, 0, 0, 0))
    f[(-1,  0)] = CoeffTuple((0, 1, 0, 0))
    f[( 0, -1)] = CoeffTuple((0, 0, 1, 0))
    f[(-1, -1)] = CoeffTuple((0, 0, 0, 1))

    # axes
    for i in range(1, half + 1):
        f[(i,  0)] = f[(i-1,  0)] + f[(i-2,  0)]
        f[(i, -1)] = f[(i-1, -1)] + f[(i-2, -1)]
    for i in range(-2, -(half + 2), -1):
        f[(i,  0)] = f[(i+2,  0)] - f[(i+1,  0)]
        f[(i, -1)] = f[(i+2, -1)] - f[(i+1, -1)]
    for j in range(1, half + 1):
        f[( 0, j)] = f[( 0, j-1)] + f[( 0, j-2)]
        f[(-1, j)] = f[(-1, j-1)] + f[(-1, j-2)]
    for j in range(-2, -(half + 2), -1):
        f[( 0, j)] = f[( 0, j+2)] - f[( 0, j+1)]
        f[(-1, j)] = f[(-1, j+2)] - f[(-1, j+1)]

    # four quadrants
    for i in range(1, half + 1):
        for j in range(1, half + 1):
            f[(i, j)] = f[(i-1, j)] + f[(i-2, j)]
    for i in range(-2, -(half + 2), -1):
        for j in range(1, half + 1):
            f[(i, j)] = f[(i+2, j)] - f[(i+1, j)]
    for i in range(1, half + 1):
        for j in range(-2, -(half + 2), -1):
            f[(i, j)] = f[(i, j+2)] - f[(i, j+1)]
    for i in range(-2, -(half + 2), -1):
        for j in range(-2, -(half + 2), -1):
            f[(i, j)] = f[(i+2, j)] - f[(i+1, j)]

    return f


def make_2dseq(a: int, b: int, c: int, d: int, half: int = 15) -> dict:
    """
    Build a 2D generalised Fibonacci grid centred at (0,0).

    Seed block:
        f( 0, 0) = a    f(-1, 0) = b
        f( 0,-1) = c    f(-1,-1) = d

    Returns a dict keyed by (i, j) covering i,j in [-(half+1), half].
    """
    f = {}
    f[(0, 0)], f[(-1, 0)], f[(0, -1)], f[(-1, -1)] = a, b, c, d

    # axes
    for i in range(1, half + 1):
        f[(i,  0)] = f[(i - 1,  0)] + f[(i - 2,  0)]
        f[(i, -1)] = f[(i - 1, -1)] + f[(i - 2, -1)]
    for i in range(-2, -(half + 2), -1):
        f[(i,  0)] = f[(i + 2,  0)] - f[(i + 1,  0)]
        f[(i, -1)] = f[(i + 2, -1)] - f[(i + 1, -1)]
    for j in range(1, half + 1):
        f[( 0, j)] = f[( 0, j - 1)] + f[( 0, j - 2)]
        f[(-1, j)] = f[(-1, j - 1)] + f[(-1, j - 2)]
    for j in range(-2, -(half + 2), -1):
        f[( 0, j)] = f[( 0, j + 2)] - f[( 0, j + 1)]
        f[(-1, j)] = f[(-1, j + 2)] - f[(-1, j + 1)]

    # four quadrants
    for i in range(1, half + 1):
        for j in range(1, half + 1):
            f[(i, j)] = f[(i - 1, j)] + f[(i - 2, j)]
    for i in range(-2, -(half + 2), -1):
        for j in range(1, half + 1):
            f[(i, j)] = f[(i + 2, j)] - f[(i + 1, j)]
    for i in range(1, half + 1):
        for j in range(-2, -(half + 2), -1):
            f[(i, j)] = f[(i, j + 2)] - f[(i, j + 1)]
    for i in range(-2, -(half + 2), -1):
        for j in range(-2, -(half + 2), -1):
            f[(i, j)] = f[(i + 2, j)] - f[(i + 1, j)]

    return f
