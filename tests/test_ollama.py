"""Tes klien Ollama (httpx MockTransport) termasuk dukungan API key."""

import json

import httpx
import pytest
from langchain.messages import HumanMessage, SystemMessage, ToolMessage

from greth.config import CLOUD_URL, DEFAULT_BASE_URL, LlmConfig
from llm.chat import OllamaChat, to_wire
from llm.ollama import OllamaClient, OllamaError
from tools.evaluate.tool import evaluate


def make_client(handler, *, key: str | None, host: str = CLOUD_URL) -> OllamaClient:
    cfg = LlmConfig(model="m", base_url=host, api_key=key)
    return OllamaClient(cfg, transport=httpx.MockTransport(handler))


async def test_authorization_header_only_with_key() -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json={"models": [{"name": "gpt-oss:120b"}]})

    assert await make_client(handler, key="secret").list_models() == ["gpt-oss:120b"]
    await make_client(handler, key=None, host=DEFAULT_BASE_URL).list_models()
    assert seen[0].headers["Authorization"] == "Bearer secret"
    assert "Authorization" not in seen[1].headers


async def test_web_search_requires_key_and_sends_no_request() -> None:
    called = False

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal called
        called = True
        return httpx.Response(200, json={})

    with pytest.raises(OllamaError, match="--key"):
        await make_client(handler, key=None, host=DEFAULT_BASE_URL).web_search("x", 5)
    assert not called


async def test_web_search_goes_to_cloud_and_caps_results() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert str(request.url) == f"{CLOUD_URL}/api/web_search"
        assert request.headers["Authorization"] == "Bearer k"
        assert json.loads(request.content) == {"query": "q", "max_results": 10}
        return httpx.Response(200, json={"results": [{"title": "t", "url": "u", "content": "c"}]})

    rows = await make_client(handler, key="k", host=DEFAULT_BASE_URL).web_search("q", 99)
    assert rows[0]["url"] == "u"


async def test_unauthorized_is_explained() -> None:
    client = make_client(lambda request: httpx.Response(401, json={"error": "no"}), key="bad")
    with pytest.raises(OllamaError, match="--key"):
        await client.chat("m", [], None)


async def test_chat_model_roundtrip_with_tool_call() -> None:
    payloads: list[dict] = []

    def handler(request: httpx.Request) -> httpx.Response:
        payloads.append(json.loads(request.content))
        message = {
            "role": "assistant",
            "content": "",
            "tool_calls": [{"function": {"name": "evaluate", "arguments": {"observed": "o", "feedback": "f", "success": True}}}],
        }
        return httpx.Response(200, json={"message": message})

    model = OllamaChat(client=make_client(handler, key="k"), model="gpt-oss:120b")
    reply = await model.bind_tools([evaluate]).ainvoke([SystemMessage("s"), HumanMessage("u")])

    assert reply.tool_calls[0]["name"] == "evaluate"
    assert reply.tool_calls[0]["args"] == {"observed": "o", "feedback": "f", "success": True}
    assert reply.tool_calls[0]["id"]
    assert payloads[0]["model"] == "gpt-oss:120b"
    assert payloads[0]["stream"] is False
    assert payloads[0]["tools"][0]["function"]["name"] == "evaluate"
    assert payloads[0]["tools"][0]["function"]["description"]


def test_tool_message_carries_tool_name() -> None:
    wire = to_wire([ToolMessage(content="err", tool_call_id="1", name="evaluate")])
    assert wire == [{"role": "tool", "content": "err", "tool_name": "evaluate"}]
