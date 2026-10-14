"""Tes klien Ollama (httpx MockTransport): auth header dan round-trip chat."""

import json

import httpx
import pytest
from langchain.messages import HumanMessage, SystemMessage, ToolMessage

from greth.config import DEFAULT_BASE_URL, LlmConfig
from llm.chat import OllamaChat, to_wire
from llm.ollama import OllamaClient, OllamaError
from tools.evaluate.tool import evaluate


def make_client(handler, *, key: str | None, base_url: str = DEFAULT_BASE_URL) -> OllamaClient:
    cfg = LlmConfig(model="m", base_url=base_url, api_key=key)
    return OllamaClient(cfg, transport=httpx.MockTransport(handler))


async def test_authorization_header_only_with_key() -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json={"models": [{"name": "qwen3:8b"}]})

    assert await make_client(handler, key="secret").list_models() == ["qwen3:8b"]
    await make_client(handler, key=None).list_models()
    assert seen[0].headers["Authorization"] == "Bearer secret"
    assert "Authorization" not in seen[1].headers


async def test_unauthorized_is_explained() -> None:
    client = make_client(lambda request: httpx.Response(401, json={"error": "no"}), key="bad")
    with pytest.raises(OllamaError, match="--key"):
        await client.chat("m", [], None)


async def test_connection_error_is_wrapped() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("boom", request=request)

    client = make_client(handler, key=None, base_url="http://127.0.0.1:1")
    with pytest.raises(OllamaError, match="ConnectError"):
        await client.list_models()


async def test_chat_model_roundtrip_with_tool_call() -> None:
    payloads: list[dict] = []

    def handler(request: httpx.Request) -> httpx.Response:
        payloads.append(json.loads(request.content))
        message = {
            "role": "assistant",
            "content": "",
            "tool_calls": [
                {
                    "function": {
                        "name": "evaluate",
                        "arguments": {"observed": "o", "feedback": "f", "success": True, "next": True, "to_leader": False},
                    }
                }
            ],
        }
        return httpx.Response(200, json={"message": message})

    model = OllamaChat(client=make_client(handler, key="k"), model="qwen3:8b")
    reply = await model.bind_tools([evaluate]).ainvoke([SystemMessage("s"), HumanMessage("u")])

    assert reply.tool_calls[0]["name"] == "evaluate"
    assert reply.tool_calls[0]["args"] == {
        "observed": "o",
        "feedback": "f",
        "success": True,
        "next": True,
        "to_leader": False,
    }
    assert reply.tool_calls[0]["id"]
    assert payloads[0]["model"] == "qwen3:8b"
    assert payloads[0]["stream"] is False
    assert payloads[0]["tools"][0]["function"]["name"] == "evaluate"
    assert payloads[0]["tools"][0]["function"]["description"]


def test_tool_message_carries_tool_name() -> None:
    wire = to_wire([ToolMessage(content="err", tool_call_id="1", name="evaluate")])
    assert wire == [{"role": "tool", "content": "err", "tool_name": "evaluate"}]
