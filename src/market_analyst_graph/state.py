from operator import add
from typing import Annotated, List, Any, TypedDict, Optional

from langgraph.graph import add_messages

from market_analyst_graph.structured_outputs import AnalysisOutput


class State(TypedDict):
    messages: Annotated[List[Any], add_messages]
    mcp_tools_used: Annotated[List[str], add]
    results: Annotated[Optional[AnalysisOutput], add]