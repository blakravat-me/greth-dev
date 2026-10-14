"""Ekstraksi judul dan teks dari HTML tanpa dependensi tambahan."""

from html.parser import HTMLParser

_SKIP = {"script", "style", "noscript", "svg"}


class _Extractor(HTMLParser):
    """Kumpulkan teks tampak dan judul halaman."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title = ""
        self._chunks: list[str] = []
        self._skip = 0
        self._in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in _SKIP:
            self._skip += 1
        elif tag == "title":
            self._in_title = True

    def handle_endtag(self, tag: str) -> None:
        if tag in _SKIP:
            self._skip = max(0, self._skip - 1)
        elif tag == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        text = data.strip()
        if self._skip or not text:
            return
        if self._in_title:
            self.title += text
        else:
            self._chunks.append(text)

    @property
    def text(self) -> str:
        """Teks gabungan satu baris."""
        return " ".join(self._chunks)


def extract(html: str) -> tuple[str, str]:
    """Kembalikan (judul, teks) dari dokumen HTML."""
    parser = _Extractor()
    parser.feed(html)
    parser.close()
    return parser.title, parser.text
