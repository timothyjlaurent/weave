import typing

from ..api import type, op, use
from ..weave_types import Function, Float
from ..ops_primitives import Number

from ..weave_internal import define_fn, call_fn, make_const_node


@type()
class NumberBin:
    start: float
    stop: float


@op(
    input_type={"step": Float()},
    output_type=Function(
        input_types={"row": Float()},
        output_type=NumberBin.WeaveType(),  # type: ignore
    ),
)
def number_bins_fixed(step):
    def body(row):
        if step <= 0:
            raise ValueError("Step must be greater than zero.")
        mult = 1.0 / step
        start_node = Number.floor(row * mult) / mult
        return make_number_bin(
            start=start_node, stop=start_node + step
        )  # dict_ops.dict_(start=start_node, stop=start_node + step)

    # need to call use because define_fn returns a constNode
    # where the val is an outputNode
    return use(define_fn({"row": Float()}, body))


@op(
    output_type=Function(
        input_types={"row": Float()}, output_type=NumberBin.WeaveType()  # type: ignore
    )
)
def numbers_bins_equal(arr: typing.List[float], bins: float):
    arr_min = min(arr) if len(arr) > 0 else 0
    arr_max = max(arr) if len(arr) > 0 else 0
    step = (arr_max - arr_min) / bins
    return use(number_bins_fixed(step))


@op(
    input_type={
        "in_": Float(),
        "bin_fn": Function(
            input_types={"row": Float()}, output_type=NumberBin.WeaveType()  # type: ignore
        ),
    }
)
def number_bin(in_, bin_fn) -> NumberBin:
    result = use(call_fn(bin_fn, {"row": make_const_node(Float(), in_)}))
    return result


@op()
def make_number_bin(start: float, stop: float) -> NumberBin:
    return NumberBin(start, stop)
