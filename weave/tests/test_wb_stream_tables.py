import time
import pytest
import weave
from weave import weave_types
from weave.wandb_interface.wandb_stream_table import StreamTable
import numpy as np
from PIL import Image


# Example of end to end integration test
def test_stream_logging(user_by_api_key_in_env):
    st = StreamTable(
        "test_table",
        project_name="stream-tables",
        entity_name=user_by_api_key_in_env.username,
    )
    for i in range(10):
        st.log({"hello": f"world_{i}", "index": i, "nested": {"a": [i]}})
    st.finish()

    hist_node = (
        weave.ops.project(user_by_api_key_in_env.username, "stream-tables")
        .run("test_table")
        .history2()
    )

    exp_type = weave_types.TypedDict({"a": weave_types.List(weave_types.Int())})
    nested_type = hist_node.type.value.object_type.property_types["nested"].members[1]
    assert exp_type.assign_type(nested_type)
    assert weave.use(hist_node["hello"]).to_pylist_tagged() == [
        f"world_{i}" for i in range(10)
    ]
    assert weave.use(hist_node["index"]).to_pylist_tagged() == [i for i in range(10)]
    assert weave.use(hist_node["nested"]).to_pylist_tagged() == [
        {"a": [i]} for i in range(10)
    ]


def test_stream_logging_image(user_by_api_key_in_env):
    def image():
        imarray = np.random.rand(100, 100, 3) * 255
        return Image.fromarray(imarray.astype("uint8")).convert("RGBA")

    st = StreamTable(
        "test_table-8",
        project_name="stream-tables",
        entity_name=user_by_api_key_in_env.username,
    )
    for i in range(3):
        st.log({"image": image()})
    st.finish()

    # There is a race case here. For some reason, there is a lag between file uploading
    # and the W&B server being able to properly authenticate the file download request.
    # In lieu of a proper polling/waiting mechanism, we just sleep for a bit. UGLY!
    time.sleep(5)

    hist_node = (
        weave.ops.project(user_by_api_key_in_env.username, "stream-tables")
        .run("test_table-8")
        .history2()
    )

    images = weave.use(hist_node["image"]).to_pylist_tagged()
    assert len(images) == 3
    assert (np.array(images[0]) != np.array(images[1])).any()
    assert isinstance(images[0], Image.Image)


def test_multi_writers_sequential(user_by_api_key_in_env):
    st = StreamTable(
        "test_table",
        project_name="stream-tables",
        entity_name=user_by_api_key_in_env.username,
    )
    for i in range(10):
        st.log({"index": i, "writer": "a"})
    st.finish()

    st = StreamTable(
        "test_table",
        project_name="stream-tables",
        entity_name=user_by_api_key_in_env.username,
    )
    for i in range(10):
        st.log({"index": 10 + i, "writer": "b"})
    st.finish()

    time.sleep(3)

    hist_node = (
        weave.ops.project(user_by_api_key_in_env.username, "stream-tables")
        .run("test_table")
        .history2()
    )
    assert weave.use(hist_node["index"]).to_pylist_tagged() == [i for i in range(20)]
    assert weave.use(hist_node["writer"]).to_pylist_tagged() == [
        "a" for i in range(10)
    ] + ["b" for i in range(10)]
    assert weave.use(hist_node["_step"]).to_pylist_tagged() == [i for i in range(20)]


@pytest.mark.skip(reason="This is expected to fail until W&B updates step management")
def test_multi_writers_parallel(user_by_api_key_in_env):
    st_1 = StreamTable(
        "test_table",
        project_name="stream-tables",
        entity_name=user_by_api_key_in_env.username,
    )
    st_2 = StreamTable(
        "test_table",
        project_name="stream-tables",
        entity_name=user_by_api_key_in_env.username,
    )

    indexes = []
    writers = []

    for i in range(5):
        st_1.log({"index": i * 2, "writer": "a"})
        st_2.log({"index": i * 2 + 1, "writer": "b"})
        indexes.append(i * 2)
        indexes.append(i * 2 + 1)
        writers.append("a")
        writers.append("b")
    st_1.finish()
    st_2.finish()

    hist_node = (
        weave.ops.project(user_by_api_key_in_env.username, "stream-tables")
        .run("test_table")
        .history2()
    )
    assert weave.use(hist_node["index"]) == indexes
    assert weave.use(hist_node["writer"]) == writers
    assert weave.use(hist_node["_step"]) == [i for i in range(20)]
