"""
Functions for inferring Weave Types from Python types.
"""

import collections
import types
import typing
import typing_extensions

from . import weave_types
from . import graph


class TypedDictLike:
    __required_keys__: frozenset[str]


def is_typed_dict_like(t: type) -> typing_extensions.TypeGuard[TypedDictLike]:
    return hasattr(t, "__required_keys__")


def simple_python_type_to_type(py_type: type):
    types = weave_types.instance_class_to_potential_type(py_type)
    if not types:
        return weave_types.UnknownType()
    return types[-1]  # last Type is most specific


def python_type_to_type(
    py_type: typing.Union[types.GenericAlias, type]
) -> weave_types.Type:
    if py_type == weave_types.Type:
        return weave_types.Type()
    elif py_type == typing.Any:
        return weave_types.Any()
    elif isinstance(py_type, types.GenericAlias) or isinstance(
        py_type, typing._GenericAlias  # type: ignore
    ):
        args = [python_type_to_type(a) for a in py_type.__args__]
        if py_type.__origin__ == list or py_type.__origin__ == collections.abc.Sequence:
            return weave_types.List(*args)
        elif py_type.__origin__ == dict:
            return weave_types.Dict(*args)
        elif py_type.__origin__ == graph.Node:
            return weave_types.Function({}, args[0])
        else:
            return weave_types.UnknownType()
    elif is_typed_dict_like(py_type):
        return weave_types.TypedDict(
            {
                k: python_type_to_type(py_type.__annotations__[k])
                for k in py_type.__required_keys__
            }
        )
    weave_type = simple_python_type_to_type(py_type)
    if weave_type == weave_types.UnknownType():
        return weave_type
    return weave_type()
