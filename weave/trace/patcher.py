from typing import Any, Callable, Optional

class Patcher():
    def attempt_patch(self):
        pass

    def undo_patch(self):
        pass

class MultiPatcher(Patcher):
    def __init__(self, patchers: list[Patcher]) -> None:
        self.patchers = patchers

    def attempt_patch(self) -> None:
        for patcher in self.patchers:
            patcher.attempt_patch()

    def undo_patch(self) -> None:
        for patcher in self.patchers:
            patcher.undo_patch()


class _SymbolTarget:
    def __init__(self, base_symbol: Any, attr: str) -> None:
        self.base_symbol = base_symbol
        self.attr = attr


class SymbolPatcher:
    _get_base_symbol: Callable
    _attribute_name: str
    _make_new_value: Callable
    _original_value: Any = None
    _patched_applied: bool = False

    def __init__(
        self, get_base_symbol: Callable, attribute_name: str, make_new_value: Callable
    ) -> None:
        self._get_base_symbol = get_base_symbol
        self._attribute_name = attribute_name
        self._make_new_value = make_new_value

    def _get_symbol_target(self) -> Optional[_SymbolTarget]:
        base_symbol = self._get_base_symbol()
        if base_symbol is None:
            return None
        parts = self._attribute_name.split(".")
        for part in parts[:-1]:
            try:
                base_symbol = getattr(base_symbol, part)
            except AttributeError:
                return None
        attr = parts[-1]
        return _SymbolTarget(base_symbol, attr)

    def attempt_patch(self) -> bool:
        if self._patched_applied:
            return True
        target = self._get_symbol_target()
        if target is None:
            return False
        self._original_value = getattr(target.base_symbol, target.attr)
        setattr(
            target.base_symbol,
            target.attr,
            self._make_new_value(self._original_value),
        )
        self._patched_applied = True
        return True

    def undo_patch(self) -> bool:
        if not self._patched_applied:
            return False
        target = self._get_symbol_target()
        if target is None:
            return False

        setattr(target.base_symbol, target.attr, self._original_value)
        self._patched_applied = False
        return True
