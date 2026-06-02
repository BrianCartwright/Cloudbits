from dataclasses import dataclass, field


@dataclass
class SatelliteSet:
    coordinates: set = field(default_factory=set)   # {(row, col), ...}
    handle_row: int = 0
    handle_col: int = 0
    active: bool = True
    # animation_state is a runtime display attribute; never stored here


class CellSetManager:
    """
    Manages Build cell set and Satellite cell sets as separate collections.
    Each Satellite set is a distinct SatelliteSet instance — never a single
    monolithic set.  Phase 1 uses Build cells only; Satellite support is
    Phase 3a.
    """

    def __init__(self) -> None:
        self.build_cells: set = set()          # {(row, col), ...}
        self.satellite_sets: list = []         # [SatelliteSet, ...]
        self._active_idx: int = -1

    def toggle_build_cell(self, row: int, col: int) -> None:
        coord = (row, col)
        if coord in self.build_cells:
            self.build_cells.discard(coord)
        else:
            self.build_cells.add(coord)

    @property
    def active_satellite(self):
        if 0 <= self._active_idx < len(self.satellite_sets):
            return self.satellite_sets[self._active_idx]
        return None

    def snapshot(self) -> dict:
        """Serialisable snapshot of all cell state."""
        return {
            "build_cells": frozenset(self.build_cells),
            "satellite_sets": [
                {
                    "coordinates": frozenset(s.coordinates),
                    "handle_row": s.handle_row,
                    "handle_col": s.handle_col,
                    "active": s.active,
                }
                for s in self.satellite_sets
            ],
            "active_idx": self._active_idx,
        }
