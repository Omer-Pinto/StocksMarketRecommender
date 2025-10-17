from operator import add
from typing import Annotated, List, Any, TypedDict

from langgraph.graph import add_messages
from pydantic import BaseModel


class State(TypedDict):
    messages: Annotated[List[Any], add_messages]
    mcp_tools_used: Annotated[List[str], add]