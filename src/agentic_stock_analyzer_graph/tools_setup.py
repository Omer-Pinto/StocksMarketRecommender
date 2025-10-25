import os
from typing import List
import asyncio
from tools import *

async def tools_setup() -> List[ToolsWrapper]:
    output_directory = "outputs"
    os.makedirs(output_directory, exist_ok=True)
    tools_wrappers = [PushNotificationTool(), YahooFinanceMCPTools(), FileManagementToolkitWrapper(output_directory)]
    await asyncio.gather(*(tool.setup() for tool in tools_wrappers))
    return tools_wrappers

async def tools_cleanup(tools_wrappers: List[ToolsWrapper]) -> None:
    await asyncio.gather(*(tool.cleanup() for tool in tools_wrappers))


