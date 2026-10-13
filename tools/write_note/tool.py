"""Tool Operator: menulis catatan atau jawaban teks."""

from langchain.tools import tool

from tools.policy import ToolOutput, register
from tools.write_note.schema import WriteNoteArgs


@register("operator")
@tool("write_note", args_schema=WriteNoteArgs)
async def write_note(title: str, body: str, displaying: bool = False) -> list[ToolOutput]:
    """Tulis catatan atau jawaban teks; displaying=true menampilkannya ke pengguna."""
    return [ToolOutput(title=title, body=body, displaying=displaying)]
