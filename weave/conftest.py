import os
import random
import numpy as np

import pathlib
import typing
import pytest
import shutil
import tempfile

import weave

from . import context_state
from .tests import fixture_fakewandb
from . import serialize
from . import client as client_legacy
from .language_features.tagging.tag_store import isolated_tagging_context
from . import logs
from . import io_service
from . import logs
from . import environment
import logging

from flask.testing import FlaskClient

from .tests.wandb_system_tests_conftest import *
from .tests.trace_server_clickhouse_conftest import *

from weave.trace_server import (
    sqlite_trace_server,
    trace_server_interface,
    remote_http_trace_server,
)
from weave import weave_init

logs.configure_logger()

# Lazy mode was the default for a long time. Eager is now the default for the user API.
# A lot of tests are written to expect lazy mode, so just make lazy mode the default for
# tests.
context_state._eager_mode.set(False)

# A lot of tests rely on weave.ops.* being in scope. Importing this here
# makes that work...
from weave import ops


### Disable datadog engine tracing


class FakeTracer:
    def trace(*args, **kwargs):
        pass


def make_fake_tracer():
    return FakeTracer()


from . import engine_trace


### End disable datadog engine tracing

### disable internet access

import socket


def guard(*args, **kwargs):
    raise Exception("I told you not to use the Internet!")


### End disable internet access

# Uncomment these two lines to disable internet access entirely.
# engine_trace.tracer = make_fake_tracer
# socket.socket = guard


def pytest_sessionstart(session):
    context_state.disable_analytics()


@pytest.fixture()
def test_artifact_dir():
    return "/tmp/weave/pytest/%s" % os.environ.get("PYTEST_CURRENT_TEST")


def pytest_collection_modifyitems(config, items):
    # Get the job number from environment variable (0 for even tests, 1 for odd tests)
    job_num = config.getoption("--job-num", default=None)
    if job_num is None:
        return

    job_num = int(job_num)

    selected_items = []
    for index, item in enumerate(items):
        if index % 2 == job_num:
            selected_items.append(item)

    items[:] = selected_items


@pytest.fixture(autouse=True)
def pre_post_each_test(test_artifact_dir, caplog):
    # TODO: can't get this to work. I was trying to setup pytest log capture
    # to use our custom log stuff, so that it indents nested logs properly.
    caplog.handler.setFormatter(logging.Formatter(logs.default_log_format))
    # Tests rely on full cache mode right now.
    os.environ["WEAVE_CACHE_MODE"] = "full"
    os.environ["WEAVE_GQL_SCHEMA_PATH"] = str(
        pathlib.Path(__file__).parent.parent / "wb_schema.gql"
    )
    try:
        shutil.rmtree(test_artifact_dir)
    except (FileNotFoundError, OSError):
        pass
    os.environ["WEAVE_LOCAL_ARTIFACT_DIR"] = test_artifact_dir
    with isolated_tagging_context():
        yield
    del os.environ["WEAVE_LOCAL_ARTIFACT_DIR"]


@pytest.fixture(autouse=True)
def throw_on_error():
    os.environ["WEAVE_VALUE_OR_ERROR_DEBUG"] = "true"
    yield
    del os.environ["WEAVE_VALUE_OR_ERROR_DEBUG"]


@pytest.fixture()
def cache_mode_minimal():
    os.environ["WEAVE_NO_CACHE"] = "true"
    yield
    del os.environ["WEAVE_NO_CACHE"]


@pytest.fixture()
def fresh_server_logfile():
    def _clearlog():
        try:
            os.remove(logs.default_log_filename())
        except (OSError, FileNotFoundError) as e:
            pass

    _clearlog()
    yield
    _clearlog()


@pytest.fixture()
def cereal_csv():
    with tempfile.TemporaryDirectory() as d:
        cereal_path = os.path.join(d, "cereal.csv")
        shutil.copy("testdata/cereal.csv", cereal_path)
        yield cereal_path


@pytest.fixture()
def eager_mode():
    with context_state.eager_execution():
        yield


@pytest.fixture()
def fake_wandb():
    setup_response = fixture_fakewandb.setup()
    yield setup_response
    fixture_fakewandb.teardown(setup_response)


@pytest.fixture()
def use_server_gql_schema():
    old_schema_path = environment.gql_schema_path()
    if old_schema_path is not None:
        del os.environ["WEAVE_GQL_SCHEMA_PATH"]
    yield
    if old_schema_path is not None:
        os.environ["WEAVE_GQL_SCHEMA_PATH"] = old_schema_path


@pytest.fixture()
def fixed_random_seed():
    random.seed(8675309)
    np.random.seed(8675309)
    yield
    random.seed(None)
    np.random.seed(None)


@pytest.fixture()
def app():
    from . import weave_server

    app = weave_server.make_app()
    app.config.update(
        {
            "TESTING": True,
        }
    )

    yield app


class HttpServerTestClient:
    def __init__(self, flask_test_client: FlaskClient):
        """Constructor.

        Args:
            flask_test_client: A flask test client to use for sending requests to the test application
        """
        self.flask_test_client = flask_test_client
        self.execute_endpoint = "/__weave/execute"

    def execute(
        self,
        nodes,
        headers: typing.Optional[dict[str, typing.Any]] = None,
        no_cache=False,
    ):
        _headers: dict[str, typing.Any] = {}
        if headers is not None:
            _headers = headers

        serialized = serialize.serialize(nodes)
        r = self.flask_test_client.post(
            self.execute_endpoint,
            json={"graphs": serialized},
            headers=_headers,
        )

        return r.json["data"]


@pytest.fixture()
def http_server_test_client(app):
    from . import weave_server

    app = weave_server.make_app()
    flask_client = app.test_client()
    return HttpServerTestClient(flask_client)


@pytest.fixture()
def weave_test_client(http_server_test_client):
    return client_legacy.Client(http_server_test_client)


@pytest.fixture()
def enable_touch_on_read():
    os.environ["WEAVE_ENABLE_TOUCH_ON_READ"] = "1"
    yield
    del os.environ["WEAVE_ENABLE_TOUCH_ON_READ"]


@pytest.fixture()
def io_server_factory():
    original_server = io_service.SERVER

    def factory(process=False):
        server = io_service.Server(process=process)
        server.start()
        io_service.SERVER = server
        return server

    yield factory

    if io_service.SERVER and io_service.SERVER is not original_server:
        io_service.SERVER.shutdown()

    io_service.SERVER = original_server


@pytest.fixture()
def consistent_table_col_ids():
    from weave.panels import table_state

    with table_state.use_consistent_col_ids():
        yield


@pytest.fixture()
def ref_tracking():
    with context_state.ref_tracking(True):
        yield


@pytest.fixture()
def strict_op_saving():
    with context_state.strict_op_saving(True):
        yield


# we already were doing pytest_addoption in wandb_system_tests_conftest so
# the weave flag is there as well
# def pytest_addoption(parser):
#     parser.addoption(
#         "--weave-server",
#         action="store",
#         default="sqlite",
#         help="Specify the client object to use: sqlite or clickhouse",
#     )


@pytest.fixture()
def client(request) -> Generator[weave_client.WeaveClient, None, None]:
    weave_server_flag = request.config.getoption("--weave-server")
    tsi: trace_server_interface.TraceServerInterface
    if weave_server_flag == "sqlite":
        sql_lite_server = sqlite_trace_server.SqliteTraceServer(
            "file::memory:?cache=shared"
        )
        sql_lite_server.drop_tables()
        sql_lite_server.setup_tables()
        tsi = sql_lite_server
    elif weave_server_flag == "clickhouse":
        ch_server = clickhouse_trace_server_batched.ClickHouseTraceServer.from_env(
            use_async_insert=False
        )
        ch_server.ch_client.command("DROP DATABASE IF EXISTS db_management")
        ch_server.ch_client.command("DROP DATABASE IF EXISTS default")
        ch_server._run_migrations()
        tsi = ch_server
    elif weave_server_flag.startswith("http"):
        remote_server = remote_http_trace_server.RemoteHTTPTraceServer(
            weave_server_flag
        )
        tsi = remote_server

    client = weave_client.WeaveClient("shawn", "test-project", tsi)
    inited_client = weave_init.InitializedClient(client)
    try:
        yield inited_client.client
    finally:
        inited_client.reset()
