import asyncio
import pytest
from .. import io_service
from .. import filesystem
import time


@pytest.mark.asyncio
@pytest.mark.parametrize("process", [True, False])
async def test_io_service_async_client(io_server_factory, process):

    server: io_service.Server = io_server_factory(process)
    client = io_service.AsyncClient(
        server=server,
    )

    loop = asyncio.get_running_loop()

    results = []
    tasks = set()
    start = time.time()
    async with client.connect() as conn:
        for _ in range(10):
            task = loop.create_task(conn.sleep(0.1))
            tasks.add(task)

            def task_done_callback(fut):
                results.append(fut.result())

            task.add_done_callback(task_done_callback)
        await asyncio.wait(tasks)

    end = time.time()

    assert len(results) == 10

    # if serial, this should be greater than 1 second (10 * 0.1)
    # if executed concurrently, this should be between 0.1 and 0.2 (0.1 + overhead)
    assert 0.1 < end - start < 0.2
    for result in results:
        assert result == 0.1

    assert not conn.connected
    assert len(server.client_response_queues) == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("process", [True, False])
async def test_io_service_sync_client(io_server_factory, process):

    server: io_service.Server = io_server_factory(process)
    fs = filesystem.get_filesystem()
    client = io_service.SyncClient(
        server=server,
        fs=fs,
    )

    start = time.time()
    results = []
    for _ in range(10):
        results.append(client.sleep(0.1))
    end = time.time()

    assert len(results) == 10

    # if serial, this should be greater than 1 second (10 * 0.1)
    # if executed concurrently, this should be between 0.1 and 0.2 (0.1 + overhead)
    assert 1 < end - start < 1.1
    for result in results:
        assert result == 0.1

    assert len(server.client_response_queues) == 0
