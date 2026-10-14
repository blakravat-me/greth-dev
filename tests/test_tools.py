"""Tes unit tool Operator: internet_search (ddgs) dan read_url (httpx + ekstraksi)."""

import httpx
import pytest

import tools.internet_search.tool as search_tool
import tools.read_url.tool as read_tool
from helpers.html_text import extract


class FakeDDGS:
    def __init__(self) -> None:
        pass

    def text(self, query: str, max_results: int) -> list[dict[str, str]]:
        assert max_results == 5
        return [{"href": "https://x.test", "title": "Judul", "body": "isi " * 500}]


class EmptyDDGS:
    def text(self, query: str, max_results: int) -> list[dict[str, str]]:
        return []


class BoomDDGS:
    def text(self, query: str, max_results: int) -> list[dict[str, str]]:
        raise RuntimeError("jaringan turun")


async def test_internet_search_maps_ddgs_rows(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(search_tool, "DDGS", FakeDDGS)
    rows = await search_tool.internet_search.ainvoke({"search": "q", "displaying": True})
    assert rows[0].url == "https://x.test"
    assert rows[0].title == "Judul"
    assert rows[0].displaying is True
    assert len(rows[0].body) <= 1500  # settings.body_limit


async def test_internet_search_no_results(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(search_tool, "DDGS", EmptyDDGS)
    rows = await search_tool.internet_search.ainvoke({"search": "q"})
    assert rows[0].title == "no results"


async def test_internet_search_failure_becomes_result(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(search_tool, "DDGS", BoomDDGS)
    rows = await search_tool.internet_search.ainvoke({"search": "q"})
    assert "jaringan turun" in rows[0].body


async def test_read_url_extracts_title_and_text(monkeypatch: pytest.MonkeyPatch) -> None:
    html = "<html><head><title>Judul Halaman</title></head><body><p>Halo dunia</p></body></html>"

    async def fake_get(url: str) -> httpx.Response:
        return httpx.Response(200, content=html.encode(), request=httpx.Request("GET", url))

    monkeypatch.setattr(read_tool, "_get", fake_get)
    rows = await read_tool.read_url.ainvoke({"url": "https://x.test", "displaying": True})
    assert rows[0].title == "Judul Halaman"
    assert "Halo dunia" in rows[0].body
    assert rows[0].displaying is True


async def test_read_url_http_error_becomes_result(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_get(url: str) -> httpx.Response:
        raise httpx.ConnectError("boom", request=httpx.Request("GET", url))

    monkeypatch.setattr(read_tool, "_get", fake_get)
    rows = await read_tool.read_url.ainvoke({"url": "https://x.test"})
    assert "read_url error" in rows[0].title


def test_html_text_extract_skips_script_and_style() -> None:
    html = "<html><head><title>T</title><style>.x{}</style></head><body><script>var x=1;</script><p>Isi</p></body></html>"
    title, text = extract(html)
    assert title == "T"
    assert text == "Isi"
