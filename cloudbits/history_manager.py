"""
Phase 1: HistoryManager exists and accepts K snapshots (real storage).
Phase 5: H mode navigation (Tab/Shift-Tab, Delete, Return/Escape) added here.
"""
from dataclasses import dataclass, field


@dataclass
class Snapshot:
    build_cells: frozenset
    cursor_row: int
    cursor_col: int
    mode: str           # "B" or "S"
    bingo: bool
    validation_ratio: float
    saved: bool = False  # True once this state has been saVed


class HistoryManager:

    def __init__(self) -> None:
        self._snapshots: list = []

    def keep(self, snapshot: Snapshot) -> int:
        """Append snapshot to timeline. Returns new total count."""
        self._snapshots.append(snapshot)
        return len(self._snapshots)

    @property
    def count(self) -> int:
        return len(self._snapshots)

    @property
    def snapshots(self) -> list:
        return list(self._snapshots)
