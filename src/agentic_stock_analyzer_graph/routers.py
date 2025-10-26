from langgraph.constants import END

from .state import State, Phase
from .utils import NodeName

def market_research_router(state: State) -> str:
    phase = state["analysis_phase"]
    if phase == Phase.QUERY:
        return NodeName.MARKET_ANALYST_SUBGRAPH_EXECUTER
    else:
        return NodeName.HEDGE_FUND_MANAGER
