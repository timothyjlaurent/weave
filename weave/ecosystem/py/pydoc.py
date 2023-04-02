"""Pydoc browsing.

Improvements we could make:
- Give methods chainable names (by using @weave_class and methods for auto-naming)
- Fix inability to use .name() ops
- Add more stuff
- Access attributes with getattr instead of declaring named methods.
"""

import weave
import types
import inspect


class PyModule(weave.types.Type):
    instance_classes = types.ModuleType

    def instance_to_dict(self, obj):
        return {"module_name": obj.__name__}

    def instance_from_dict(self, d):
        return __import__(d["module_name"])


class PyClass(weave.types.Type):
    # TODO: Will registering this break stuff? Everything is type.
    instance_classes = type

    def instance_to_dict(self, obj):
        return {"module_name": obj.__module__.__name__, "class_name": obj.__name__}

    def instance_from_dict(self, d):
        return getattr(__import__(d["module_name"]), d["class_name"])


class PyFunction(weave.types.Type):
    # TODO: Will registering this break stuff? Everything is type.
    instance_classes = types.FunctionType

    def instance_to_dict(self, obj):
        return {"module_name": obj.__module__.__name__, "function_name": obj.__name__}

    def instance_from_dict(self, d):
        return getattr(__import__(d["module_name"]), d["function_name"])


@weave.op()
def module_name(module: types.ModuleType) -> str:
    return module.__name__


@weave.op()
def module_doc(module: types.ModuleType) -> weave.ops.Markdown:
    return weave.ops.Markdown(module.__doc__ or "")


@weave.op()
def module_classes(module: types.ModuleType) -> list[type]:
    return [m[1] for m in inspect.getmembers(module, predicate=inspect.isclass)]


@weave.op()
def module_class(module: types.ModuleType, class_name: str) -> type:
    # TODO: type check? or have __getattr__ work instead and provide
    # refinement
    return getattr(module, class_name)


@weave.op()
def module_functions(module: types.ModuleType) -> list[types.FunctionType]:
    def is_func(m):
        return inspect.isfunction(m) or inspect.isbuiltin(m)

    return [m[1] for m in inspect.getmembers(module, predicate=is_func)]


@weave.op()
def module_function(module: types.ModuleType, function_name: str) -> types.FunctionType:
    # TODO: type check? or have __getattr__ work instead and provide
    # refinement
    return getattr(module, function_name)


@weave.op(render_info={"type": "function"})
def pyclass(module_name: str, class_name: str) -> type:
    return getattr(__import__(module_name), class_name)


@weave.op()
def pyclass_module(pyclass: type) -> types.ModuleType:
    return __import__(pyclass.__module__)


@weave.op()
def pyclass_doc(pyclass: type) -> weave.ops.Markdown:
    return weave.ops.Markdown(pyclass.__doc__ or "")


@weave.op()
def class_name(pyclass: type) -> str:
    return pyclass.__name__


@weave.op()
def class_methods(pyclass: type) -> list[types.FunctionType]:
    def is_func(m):
        return inspect.ismethod(m) or inspect.isfunction(m)

    return [m[1] for m in inspect.getmembers(pyclass, predicate=is_func)]


@weave.op()
def class_method(pyclass: type, method_name: str) -> types.FunctionType:
    return getattr(pyclass, method_name)


@weave.op()
def pyfunction(module_name: str, function_name: str) -> types.FunctionType:
    return getattr(__import__(module_name), function_name)


@weave.op()
def function_name(pyfunction: types.FunctionType) -> str:
    return pyfunction.__name__


@weave.op()
def function_doc(pyfunction: types.FunctionType) -> weave.ops.Markdown:
    return weave.ops.Markdown(pyfunction.__doc__ or "")


@weave.op()
def module_render(
    module: weave.Node[types.ModuleType],
) -> weave.panels.Card:
    return weave.panels.Card(
        title=module.module_name(),
        subtitle="python module",
        content=[
            weave.panels.CardTab(
                name="Description",
                content=weave.panels.PanelMarkdown(module.module_doc()),  # type: ignore
            ),
            weave.panels.CardTab(
                name="Classes",
                content=weave.panels.Table(
                    module.module_classes(),
                    columns=[
                        lambda c: weave.panels.WeaveLink(
                            c.class_name(),
                            to=lambda inp: module.module_class(inp),
                        )
                    ],
                ),
            ),
            weave.panels.CardTab(
                name="Functions",
                content=weave.panels.Table(
                    module.module_functions(),
                    columns=[
                        lambda c: weave.panels.WeaveLink(
                            c.function_name(),
                            to=lambda inp: module.module_function(inp),
                        )
                    ],
                ),
            ),
        ],
    )


@weave.op()
def class_render(
    cls: weave.Node[type],
) -> weave.panels.Card:
    return weave.panels.Card(
        title=cls.class_name(),
        subtitle="python class",
        content=[
            weave.panels.CardTab(
                name="Description",
                content=weave.panels.PanelMarkdown(cls.pyclass_doc()),  # type: ignore
            ),
            weave.panels.CardTab(
                name="Methods",
                content=weave.panels.Table(
                    cls.class_methods(),
                    columns=[
                        lambda m: weave.panels.WeaveLink(
                            m.function_name(),
                            to=lambda inp: cls.class_method(inp),
                        )
                    ],
                ),
            ),
        ],
    )


@weave.op()
def function_render(
    func: weave.Node[types.FunctionType],
) -> weave.panels.Card:
    return weave.panels.Card(
        title=func.function_name(),
        subtitle="python function",
        content=[
            weave.panels.CardTab(
                name="Description",
                content=weave.panels.PanelMarkdown(func.function_doc()),  # type: ignore
            ),
        ],
    )
