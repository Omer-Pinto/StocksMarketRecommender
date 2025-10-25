from langgraph.constants import END

from .state import State, Phase
from .utils import NodeName

def report_file_writer_router(state: State) -> str:
    last_message = state["messages"][-1]

    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return NodeName.REPORT_FILE_WRITER_TOOLS
    else:
        return END

def market_research_router(state: State) -> str:
    phase = state["analysis_phase"]
    if phase == Phase.QUERY:
        print("%%%market_research_router decided on MARKET_ANALYST_SUBGRAPH_EXECUTER%%%")
        return NodeName.MARKET_ANALYST_SUBGRAPH_EXECUTER
    else:
        print("%%%market_research_router decided on HEDGE_FUND_MANAGER%%%")
        return NodeName.HEDGE_FUND_MANAGER
