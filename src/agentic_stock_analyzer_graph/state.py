from enum import Enum
from operator import add
from typing import Annotated, List, Any, TypedDict, Optional

from langgraph.graph import add_messages

from .structured_outputs import FinalQueryResult, QueryRequest

class Phase(str, Enum):
    QUERY = "query"
    DECIDE = "decide"

class State(TypedDict):
    human_question: str
    analysis_phase: Phase
    messages: Annotated[List[Any], add_messages]
    queries: Annotated[List[List[QueryRequest]], add]
    analyst_query_results: Annotated[List[FinalQueryResult], add]
    decision_handoff: Optional[str]