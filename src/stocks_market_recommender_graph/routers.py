from langgraph.constants import END

from .state import State
from .utils import NodeName

def market_analyst_router(state: State) -> str:
    last_message = state["messages"][-1]

    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return NodeName.MARKET_ANALYST_TOOLS
    else:
        return NodeName.MCP_CALLS_SUMMARIZER

def report_file_writer_router(state: State) -> str:
    last_message = state["messages"][-1]

    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return NodeName.REPORT_FILE_WRITER_TOOLS
    else:
        return END