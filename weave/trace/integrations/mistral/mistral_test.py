import os
import pytest
import weave
from weave.trace_server import trace_server_interface as tsi
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from .mistral import autopatch_mistral, undo_patch_mistral

from typing import Generator

# Add to some docs, to re-record, and run:
# `MISTRAL_API_KEY=... pytest --weave-server=prod --record-mode=rewrite trace/integrations/mistral/mistral_test.py::test_mistral_quickstart`


@pytest.fixture(scope="module")
def patch_mistral() -> Generator[None, None, None]:
    autopatch_mistral()
    yield
    undo_patch_mistral()


@pytest.mark.vcr(
    filter_headers=["authorization"], allowed_hosts=["api.wandb.ai", "localhost"]
)
def test_mistral_quickstart(
    client: weave.weave_client.WeaveClient, patch_mistral: None
) -> None:
    # This is taken directly from https://docs.mistral.ai/getting-started/quickstart/
    api_key = os.environ.get("MISTRAL_API_KEY", "DUMMY_API_KEY")
    model = "mistral-large-latest"

    mistral_client = MistralClient(api_key=api_key)

    chat_response = mistral_client.chat(
        model=model,
        messages=[ChatMessage(role="user", content="What is the best French cheese?")],
    )

    res = client.server.calls_query(tsi.CallsQueryReq(project_id=client._project_id()))

    assert len(res.calls) == 1
    # Probably should do some other more robust testing here
