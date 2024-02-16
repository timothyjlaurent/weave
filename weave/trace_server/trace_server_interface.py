# Needs to be kept in sync with core/services/weave-clickhouse/src/api/interface.py

import typing
from pydantic import BaseModel
from enum import Enum


class StatusCodeEnum(str, Enum):
    UNSET='UNSET'
    OK='OK'
    ERROR='ERROR'



class CallSchema(BaseModel):
    # Identity Fields:
    entity: str
    project: str
    id: str 

    # Name of the calling function (op)
    name: str

    # Trace Context Fields

    ## Trace ID
    trace_id: str
    ## Parent ID is optional because the call may be a root
    parent_id: typing.Optional[str] = None

    # Status Fields

    ## Status Code -> UNSET, OK, ERROR
    status_code: StatusCodeEnum
    ## Start time is required
    start_time_s: float
    ## End time is optional because the call may not have finished yet
    end_time_s: typing.Optional[float] = None
    ## Exception is optional because the call may not have errored
    exception: typing.Optional[str] = None

    # Optional fields:

    ## Attributes: properties of the call
    attributes: typing.Optional[typing.Dict[str, typing.Any]] = None

    ## Inputs and Outputs
    inputs: typing.Optional[typing.Dict[str, typing.Any]] = None
    outputs: typing.Optional[typing.Dict[str, typing.Any]] = None

    ## Summary: a summary of the call
    summary: typing.Optional[typing.Dict[str, typing.Any]] = None


# YIKES! Why can't this just inherit from CallSchema and override the fields?
# These should be EXACTLY the same as CallSchema, but with some fields optional
class PartialCallForCreationSchema(BaseModel): 
    entity: str
    project: str
    id: typing.Optional[str] = None

    name: typing.Optional[str] = None

    trace_id: typing.Optional[str] = None
    parent_id: typing.Optional[str] = None
    
    status_code: typing.Optional[StatusCodeEnum] = None
    start_time_s: typing.Optional[float] = None
    end_time_s: typing.Optional[float] = None
    exception: typing.Optional[str] = None

    attributes: typing.Optional[typing.Dict[str, typing.Any]] = None
    inputs: typing.Optional[typing.Dict[str, typing.Any]] = None
    outputs: typing.Optional[typing.Dict[str, typing.Any]] = None
    summary: typing.Optional[typing.Dict[str, typing.Any]] = None


class CallCreateReq(BaseModel):
    call: PartialCallForCreationSchema

class CallCreateRes(BaseModel): 
    entity: str
    project: str
    id: str

class CallReadReq(BaseModel):
    entity: str
    project: str
    id: str
    columns: typing.Optional[typing.List[str]] = None

class CallReadRes(BaseModel):
    call: CallSchema

class _CallUpdateFields(BaseModel):
    status_code: typing.Optional[StatusCodeEnum] = None
    end_time_s: typing.Optional[float] = None
    outputs: typing.Optional[typing.Dict[str, typing.Any]] = None
    summary: typing.Optional[typing.Dict[str, typing.Any]] = None
    exception: typing.Optional[str] = None

class CallUpdateReq(BaseModel):
    entity: str
    project: str
    id: str
    fields: _CallUpdateFields

class CallUpdateRes(BaseModel): 
    entity: str
    project: str
    id: str

class CallDeleteReq(BaseModel): 
    entity: str
    project: str
    id: str

class CallDeleteRes(BaseModel): pass


class _CallsFilter(BaseModel):
    names: typing.Optional[typing.List[str]] = None
    input_object_version_refs: typing.Optional[typing.List[str]] = None
    output_object_version_refs: typing.Optional[typing.List[str]] = None
    parent_ids: typing.Optional[typing.List[str]] = None
    trace_ids: typing.Optional[typing.List[str]] = None
    call_ids: typing.Optional[typing.List[str]] = None
    trace_roots_only: typing.Optional[bool] = None
    # op_category: typing.Optional[typing.List[str]] = None

class CallsQueryReq(BaseModel): 
    entity: str
    project: str
    filter: typing.Optional[_CallsFilter] = None
    columns: typing.Optional[typing.List[str]] = None
    order_by: typing.Optional[typing.List[typing.Tuple[str, str]]] = None
    # Pagination
    # Poorman's implementation of pagination ... probably
    # should make something more sophisticated here since limit/offset
    # will not work well with high velocity data... need to provide
    # a way to avoid this (probably an "after" cursor or something like that)
    offset: typing.Optional[int] = None
    limit: typing.Optional[int] = None

class CallQueryRes(BaseModel): 
    calls: typing.List[CallSchema]

class OpCreateReq(BaseModel): pass
class OpCreateRes(BaseModel): pass
class OpReadReq(BaseModel): pass
class OpReadRes(BaseModel): pass
class OpUpdateReq(BaseModel): pass
class OpUpdateRes(BaseModel): pass
class OpDeleteReq(BaseModel): pass
class OpDeleteRes(BaseModel): pass
class OpQueryReq(BaseModel): pass
class OpQueryRes(BaseModel): pass
class ObjCreateReq(BaseModel): pass
class ObjCreateRes(BaseModel): pass
class ObjReadReq(BaseModel): pass
class ObjReadRes(BaseModel): pass
class ObjUpdateReq(BaseModel): pass
class ObjUpdateRes(BaseModel): pass
class ObjDeleteReq(BaseModel): pass
class ObjDeleteRes(BaseModel): pass
class ObjQueryReq(BaseModel): pass
class ObjQueryRes(BaseModel): pass


class TraceServerInterface:
    # Call API
    def call_create(self, req: CallCreateReq) -> CallCreateRes:
        ...
    def call_read(self, req: CallReadReq) -> CallReadRes:
        ...
    def call_update(self, req: CallUpdateReq) -> CallUpdateRes:
        ...
    def call_delete(self, req: CallDeleteReq) -> CallDeleteRes:
        ...
    def calls_query(self, req: CallsQueryReq) -> CallQueryRes:
        ...

    # Op API
    def op_create(self, req: OpCreateReq) -> OpCreateRes:
        ...
    def op_read(self, req: OpReadReq) -> OpReadRes:
        ...
    def op_update(self, req: OpUpdateReq) -> OpUpdateRes:
        ...
    def op_delete(self, req: OpDeleteReq) -> OpDeleteRes:
        ...
    def ops_query(self, req: OpQueryReq) -> OpQueryRes:
        ...

    # Obj API
    def obj_create(self, req: ObjCreateReq) -> ObjCreateRes:
        ...
    def obj_read(self, req: ObjReadReq) -> ObjReadRes:
        ...
    def obj_update(self, req: ObjUpdateReq) -> ObjUpdateRes:
        ...
    def obj_delete(self, req: ObjDeleteReq) -> ObjDeleteRes:
        ...
    def objs_query(self, req: ObjQueryReq) -> ObjQueryRes:
        ...
