from .app_state import AppState

GRID_MIN = -15
GRID_MAX = 15


class CursorController:
    """Orange Build cursor and boundary enforcement."""

    def __init__(self, state: AppState) -> None:
        self._state = state

    def move(self, dr: int, dc: int) -> bool:
        """Move cursor by (dr, dc). Returns True if movement occurred."""
        new_row = self._state.cursor_row + dr
        new_col = self._state.cursor_col + dc
        if GRID_MIN <= new_row <= GRID_MAX and GRID_MIN <= new_col <= GRID_MAX:
            self._state.cursor_row = new_row
            self._state.cursor_col = new_col
            return True
        return False

    @property
    def position(self) -> tuple:
        return (self._state.cursor_row, self._state.cursor_col)
