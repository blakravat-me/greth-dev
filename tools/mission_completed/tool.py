"""Tool Leader: menutup misi."""

from langchain.tools import tool

from tools.mission_completed.schema import Completed, MissionCompletedArgs
from tools.policy import register


@register("leader")
@tool("mission_completed", args_schema=MissionCompletedArgs)
async def mission_completed() -> Completed:
    """Tandai misi selesai; panggil hanya jika bukti sudah cukup."""
    return Completed()
