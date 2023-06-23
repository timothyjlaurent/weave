import json
import logging
import typing
import uuid

from .wandb_lite_run import InMemoryLazyLiteRun

from .. import runfiles_wandb
from .. import storage
from .. import weave_types
from .. import artifact_base

# Shawn recommended we only encode leafs, but in my testing, nested structures
# are not handled as well in in gorilla and we can do better using just weave.
# Uncomment the below to use gorilla for nested structures.
TRUST_GORILLA_FOR_NESTED_STRUCTURES = False

# Weave types are parametrized, but gorilla expects just simple strings. We could
# send the top-level string over the wire, but this fails to encode type specifics
# and therefore loses information. With this flag, we instead stringify the JSON type
# and send that over the wire. This is a bit of a hack, but it works.
ENCODE_ENTIRE_TYPE = True
TYPE_ENCODE_PREFIX = "_wt_::"


class StreamTable:
    _lite_run: InMemoryLazyLiteRun
    _table_name: str
    _project_name: str
    _entity_name: str

    _artifact: typing.Optional[runfiles_wandb.WandbRunFiles] = None

    def __init__(
        self,
        table_name: str,
        project_name: typing.Optional[str] = None,
        entity_name: typing.Optional[str] = None,
    ):
        splits = table_name.split("/")
        if len(splits) == 1:
            pass
        elif len(splits) == 2:
            if project_name is not None:
                raise ValueError(
                    f"Cannot specify project_name and table_name with '/' in it: {table_name}"
                )
            project_name = splits[0]
            table_name = splits[1]
        elif len(splits) == 3:
            if project_name is not None or entity_name is not None:
                raise ValueError(
                    f"Cannot specify project_name or entity_name and table_name with 2 '/'s in it: {table_name}"
                )
            entity_name = splits[0]
            project_name = splits[1]
            table_name = splits[2]

        # For now, we force the user to specify the entity and project
        # technically, we could infer the entity from the API key, but
        # that tends to confuse users.
        if entity_name is None or entity_name == "":
            raise ValueError(f"Must specify entity_name")
        elif project_name is None or project_name == "":
            raise ValueError(f"Must specify project_name")
        elif table_name is None or table_name == "":
            raise ValueError(f"Must specify table_name")

        job_type = "wb_stream_table"
        self._lite_run = InMemoryLazyLiteRun(
            entity_name, project_name, table_name, job_type
        )
        self._table_name = table_name
        self._project_name = project_name
        self._entity_name = entity_name

    def log(self, row_or_rows: typing.Union[dict, list[dict]]) -> None:
        if isinstance(row_or_rows, dict):
            row_or_rows = [row_or_rows]

        for row in row_or_rows:
            self._log_row(row)

    def _log_row(self, row: dict) -> None:
        self._lite_run.ensure_run()
        if self._artifact is None:
            uri = runfiles_wandb.WeaveWBRunFilesURI.from_run_identifiers(
                self._entity_name,
                self._project_name,
                self._table_name,
            )
            self._artifact = runfiles_wandb.WandbRunFiles(name=uri.name, uri=uri)
        payload = row_to_weave(row, self._artifact)
        self._lite_run.log(payload)

    def finish(self) -> None:
        self._lite_run.finish()

    def __del__(self) -> None:
        self.finish()


def maybe_history_type_to_weave_type(tc_type: str) -> typing.Optional[weave_types.Type]:
    if tc_type.startswith(TYPE_ENCODE_PREFIX):
        w_type = json.loads(tc_type[len(TYPE_ENCODE_PREFIX) :])
        return weave_types.TypeRegistry.type_from_dict(w_type)
    else:
        possible_type = weave_types.type_name_to_type(tc_type)
        if possible_type is not None:
            try:
                return possible_type()
            except Exception as e:
                logging.warning(
                    f"StreamTable Type Error: Found type for {tc_type}, but blind construction failed: {e}",
                )
    return None


def is_weave_encoded_history_cell(cell: dict) -> bool:
    return "_weave_type" in cell and "_val" in cell


def from_weave_encoded_history_cell(cell: dict) -> typing.Any:
    if not is_weave_encoded_history_cell(cell):
        raise ValueError(f"Expected weave encoded history cell, got {cell}")
    weave_json = {
        "_type": cell["_weave_type"],
        "_val": cell["_val"],
    }
    return storage.from_python(weave_json)


def row_to_weave(
    row: typing.Dict[str, typing.Any], artifact: runfiles_wandb.WandbRunFiles
) -> typing.Dict[str, typing.Any]:
    return {key: obj_to_weave(value, artifact) for key, value in row.items()}


def obj_to_weave(obj: typing.Any, artifact: runfiles_wandb.WandbRunFiles) -> typing.Any:
    def recurse(obj: typing.Any) -> typing.Any:
        return obj_to_weave(obj, artifact)

    # all primitives
    if isinstance(obj, (int, float, str, bool, type(None))):
        return obj
    else:
        if TRUST_GORILLA_FOR_NESTED_STRUCTURES:
            if isinstance(obj, dict):
                return {key: recurse(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [recurse(value) for value in obj]
            elif isinstance(obj, tuple):
                return [recurse(value) for value in obj]
            elif isinstance(obj, set):
                return [recurse(value) for value in obj]
            elif isinstance(obj, frozenset):
                return [recurse(value) for value in obj]
            else:
                return leaf_to_weave(obj, artifact)
        else:
            return leaf_to_weave(obj, artifact)


def w_type_to_type_name(w_type: typing.Union[str, dict]) -> str:
    if isinstance(w_type, str):
        return w_type
    if ENCODE_ENTIRE_TYPE:
        return TYPE_ENCODE_PREFIX + json.dumps(w_type)
    else:
        return w_type["type"]


def leaf_to_weave(
    leaf: typing.Any, artifact: runfiles_wandb.WandbRunFiles
) -> typing.Any:
    def ref_persister_artifact(
        type: weave_types.Type, refs: typing.Iterable[artifact_base.ArtifactRef]
    ) -> artifact_base.Artifact:
        # Save all the reffed objects into the new artifact.
        for mem_ref in refs:
            if mem_ref.path is not None and mem_ref._type is not None:
                # Hack: add a random salt to the end (i really want content addressing here)
                # but this is a quick fix to avoid collisions
                path = mem_ref.path + "-" + str(uuid.uuid4())
                artifact.set(path, mem_ref._type, mem_ref._obj)
        return artifact

    res = storage.to_python(leaf, None, ref_persister_artifact)

    w_type = res["_type"]
    type_name = w_type_to_type_name(w_type)

    # Optimization: If we have ENCODE_ENTIRE_TYPE=True, then we can
    # avoid re-saving the type info in _weave_type
    return {"_type": type_name, "_weave_type": res["_type"], "_val": res["_val"]}
