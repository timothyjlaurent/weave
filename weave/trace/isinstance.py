from typing import Any, TypeVar
from typing_extensions import TypeGuard

from weave.trace.object_record import ObjectRecord
from weave.trace.vals import TraceObject

C = TypeVar("C")

# TODO: need to store bases for isinstance check.


def weave_isinstance(obj: Any, cls: type[C]) -> TypeGuard[C]:
    if isinstance(obj, cls):  # type: ignore
        return True
    if isinstance(obj, ObjectRecord):
        if obj._class_name == cls.__name__:
            return True
    if isinstance(obj, TraceObject):
        if obj._class_name == cls.__name__:
            return True
    return False
