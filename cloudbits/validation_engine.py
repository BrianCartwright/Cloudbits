"""
Cloudbits validation engine — CoeffTuple algebraic backend.

Builds a coefficient grid at startup.  Each cell stores a CoeffTuple
(ca, cb, cc, cd): the seed-independent linear combination that always
produces that cell's value.  Validation is therefore universal — a Bingo
result holds for all seeds, not just a specific integer testbed.

Bingo condition: the CoeffTuple sum for the active cell set equals (k,0,0,0)
with k > 0.  The integer k is the multiplier displayed in the counter.
"""
from .seq2d import CoeffTuple, make_coeff_grid


class ValidationEngine:

    def __init__(self) -> None:
        self._coeff_grid = make_coeff_grid(half=15)

    def validate(self, cell_coords) -> tuple:
        """
        Returns (k: int, bingo: bool).

        k    — integer multiplier when bingo (sum == k * f(0,0) universally);
               0 when not bingo.
        bingo — True when the CoeffTuple sum equals (k, 0, 0, 0) with k > 0.
        """
        if not cell_coords:
            return 0, False
        total = CoeffTuple((0, 0, 0, 0))
        for r, c in cell_coords:
            total = total + self._coeff_grid[(r, c)]
        k = total.v[0]
        if k > 0 and all(v == 0 for v in total.v[1:]):
            return k, True
        return 0, False
