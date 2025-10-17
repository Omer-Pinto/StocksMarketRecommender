import json
from pathlib import Path

from langchain_core.messages import AIMessage, SystemMessage
from typing import Any, Dict

from pydantic import BaseModel

from .prompts import market_analyst_system_message, mcp_calls_summarizer_message, report_file_writer_message
from .state import State

async def market_analyst(state: State) -> Dict[str, Any]:
    system_message = market_analyst_system_message

    user_message = state["messages"][-1]

    analyst_messages = [
        SystemMessage(content=system_message),
        user_message,
    ]

    # Invoke the func-injected LLM
    response = await market_analyst.__model__.ainvoke(analyst_messages)
    mcp_tools_usages = [tool_call for tool_call in response.tool_calls] if hasattr(response, "tool_calls") and response.tool_calls else []

    # Return updated state
    return {
        "messages": [response],
        "mcp_tools_used": mcp_tools_usages,
    }

def _print_raw(response):
    print("start print raw file:")
    file = Path("outputs/raw.txt")
    with file.open("w", encoding="utf-8") as f:
        if isinstance(response, BaseModel):
            # Convert Pydantic model to dict before dumping
            json.dump(response.model_dump(), f, indent=2, ensure_ascii=False)
        else:
            json.dump(f"illegal response of type {type(response)}", f, indent=2, ensure_ascii=False)
    print("end print raw file:")

async def mcp_calls_summarizer(state: State) -> Dict[str, Any]:
    system_message = mcp_calls_summarizer_message

    mcp_tool_result_message = state["messages"][-1]
    mcp_tool_call_message = state["messages"][-2]

    summarizer_messages = [
        SystemMessage(content=system_message),
        mcp_tool_call_message,
        mcp_tool_result_message
    ]

    # Invoke the func-injected LLM
    response = await mcp_calls_summarizer.__model__.ainvoke(summarizer_messages)
    _print_raw(response)

    # Return updated state
    return {
        "messages": [AIMessage(content=response.model_dump_json())],
    }


async def report_file_writer(state: State) -> Dict[str, Any]:
    system_message = report_file_writer_message
    summary_message = state["messages"][-1]

    writer_messages = [
        SystemMessage(content=system_message),
        summary_message,
    ]

    # Invoke the LLM with structured outputs
    response = await report_file_writer.__model__.ainvoke(writer_messages)

    # Return updated state
    return {
        "messages": [response],
    }