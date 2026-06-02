from .app_state import AppState, Mode


class ModeManager:
    """B/S/H/G mode transitions and H suspension logic."""

    def __init__(self, state: AppState) -> None:
        self._state = state
        self._pre_history_mode: Mode = Mode.BUILD
        self._g_active: bool = False

    @property
    def mode(self) -> Mode:
        return self._state.mode

    @property
    def g_active(self) -> bool:
        return self._g_active

    def switch_to_build(self) -> bool:
        """Returns True if a transition occurred."""
        if self._state.mode in (Mode.BUILD, Mode.HISTORY):
            return False
        self._state.mode = Mode.BUILD
        return True

    def switch_to_satellite(self) -> bool:
        if self._state.mode in (Mode.SATELLITE, Mode.HISTORY):
            return False
        self._state.mode = Mode.SATELLITE
        return True

    def enter_history(self) -> bool:
        if self._state.mode == Mode.HISTORY:
            return False
        self._pre_history_mode = self._state.mode
        self._state.mode = Mode.HISTORY
        return True

    def exit_history(self, destructive: bool = False) -> None:
        """Restore the mode that was active before H was entered."""
        self._state.mode = self._pre_history_mode

    def toggle_grid_bg(self) -> None:
        self._g_active = not self._g_active
