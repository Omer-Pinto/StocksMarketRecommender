import json
from pathlib import Path

from langchain_core.messages import AIMessage, SystemMessage, ToolCall, ToolMessage, BaseMessage, HumanMessage
from typing import Any, Dict, List, Tuple, cast

from pydantic import BaseModel

from market_analyst_graph.prompts import market_analyst_system_message, mcp_calls_summarizer_message
from .count_tokens import count_all_messages_tokens
from .state import State

MAX_INPUT_CHARS = 2500  # tune for gpt-4o-mini (16k window)

def _clamp_text(s: str, limit=MAX_INPUT_CHARS) -> str:
    return s if len(s) <= limit else s[:limit] + "…[truncated]"

def _clamp_for_llm(message: ToolMessage, limit=MAX_INPUT_CHARS) -> ToolMessage:
    # compact serialization (no pretty-print)
    content = message.content
    compact_content = _clamp_text(content, limit)
    message.content = compact_content
    return message

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


def _get_tool_call_pairs(messages: List[BaseMessage])->Tuple[HumanMessage, AIMessage, List[ToolMessage]]:
    assert len(messages) > 2, f"summarizer called with only {len(messages)} messages"
    assert isinstance(messages[0], HumanMessage), f"summarized called with messages of unknown format - 1st message must be HumanMessage, got {type(messages[0])}"
    human_message = cast(HumanMessage, messages[0])
    assert isinstance(messages[1], AIMessage), f"summarized called with messages of unknown format - 2nd message must be AIMessage, got {type(messages[1])}"
    mcp_tool_call_message = cast(AIMessage, messages[1])
    expected_num_of_tool_calls = 0 if not hasattr(mcp_tool_call_message, "additional_kwargs") or "tool_calls" not in mcp_tool_call_message.additional_kwargs  \
        else len(mcp_tool_call_message.additional_kwargs["tool_calls"])
    assert expected_num_of_tool_calls > 0, f"expected number of tool calls is {expected_num_of_tool_calls}"
    assert len(messages) == 2 + expected_num_of_tool_calls, "total number of messages should be 2(human + ai) + num of tool calls"
    res = []
    for i in range(2, 2 + expected_num_of_tool_calls):
        assert isinstance(messages[i], ToolMessage), f"summarized called with messages of unknown format - expected {i}th message to be ToolMessage"
        res.append(_clamp_for_llm(messages[i]))
    return human_message, mcp_tool_call_message, res


async def mcp_calls_summarizer(state: State) -> Dict[str, Any]:
    print("####mcp_calls_summarizer####")
    print("total number of messages:", len(state["messages"]))

    system_message = mcp_calls_summarizer_message
    human_message, mcp_tool_call_message, mcp_tool_result_messages = _get_tool_call_pairs(state["messages"])

    summarizer_messages = [
        SystemMessage(content=system_message),
        mcp_tool_call_message,
        *mcp_tool_result_messages,
    ]

    count_all_messages_tokens(summarizer_messages)

    # Invoke the func-injected LLM
    response = await mcp_calls_summarizer.__model__.ainvoke(summarizer_messages)
    result_message = (f"mcp call summarizer was called with {len(mcp_tool_result_messages)} mcp calls to summarized  "
                      f"and summarized {len(response.calls)} results")
    # Return updated state
    return {
        "messages": [AIMessage(content=result_message)],
        "results": response,
    }
