from enum import Enum

from graph import GraphWrapper, NodeWrapper, EdgeType
from langchain_core.messages import HumanMessage
from langgraph.constants import START, END
from models import ModelWrapper, Model

from .state import State, Phase
from .structured_outputs import InvestmentDecision, ManagerDecision
from .tools_setup import tools_setup, tools_cleanup
from .node_actions import market_research_manager, market_analyst_subgraph_executer, hedge_fund_manager
from .routers import market_research_router
from .utils import NodeName

class GraphManager:
    def __init__(self):
        self.tool_wrappers = None
        self.other_tools = None
        self.graph = None
        self.node_wrappers = None
        self.model_mapping = None
        self.graph_wrapper = None
    
    async def setup(self):
        self.tool_wrappers = await tools_setup()
        self.other_tools = [
            tool
            for wrapper in self.tool_wrappers
            if wrapper.name != "yahoo_finance_mcp"
            for tool in wrapper.tools
        ]

        self._create_models()
        self._create_nodes()
        self._create_edges()

        self.graph_wrapper = GraphWrapper(
            state_type=State,   # type: ignore[assignment]
            models=list(self.model_mapping.values()),
            nodes=self.node_wrappers,
            edges_info=self.edges_info,
        )
        self.graph_wrapper.build_and_compile_graph()

    async def cleanup(self):
        await tools_cleanup(self.tool_wrappers)
        self.mcp_tools = None
        self.other_tools = None

    async def run_graph(self, query: str) -> State:
        state = {
            "human_question": query,
            "messages": [HumanMessage(content=query)],
            "analysis_phase": Phase.QUERY,
            "queries": [],
            "analyst_query_results": [],
            "decision_handoff": None,
        }
        result = await self.graph_wrapper.run_superstep(initial_state=state)
        return result

    def _create_nodes(self):
        self.node_wrappers = [
            NodeWrapper(name=NodeName.MARKET_RESEARCH_MANAGER, action=market_research_manager,
                        model_wrapper=self.model_mapping.get(NodeName.MARKET_RESEARCH_MANAGER), router=market_research_router),
            # subgraph executer is executing a graph and not using a model, so its model_wrapper isn't in use.
            NodeWrapper(name=NodeName.MARKET_ANALYST_SUBGRAPH_EXECUTER, action=market_analyst_subgraph_executer,
                        model_wrapper=self.model_mapping.get(NodeName.MARKET_RESEARCH_MANAGER)),

            NodeWrapper(name=NodeName.HEDGE_FUND_MANAGER, action=hedge_fund_manager,
                        model_wrapper=self.model_mapping.get(NodeName.HEDGE_FUND_MANAGER)),
            # NodeWrapper(name=NodeName.REPORT_WRITER_AND_NOTIFIER, action=report_file_writer,
            #             model_wrapper=self.model_mapping.get(NodeName.REPORT_WRITER_AND_NOTIFIER)),
            # ToolNodeWrapper(name=NodeName.REPORT_WRITER_AND_NOTIFIER_TOOLS, tools=self.other_tools),
        ]

    def _create_edges(self):
        self.edges_info = [
            (START, EdgeType.EDGE, [NodeName.MARKET_RESEARCH_MANAGER]),

            (NodeName.MARKET_RESEARCH_MANAGER, EdgeType.CONDITIONAL_EDGE, [NodeName.MARKET_ANALYST_SUBGRAPH_EXECUTER, NodeName.HEDGE_FUND_MANAGER]),
            (NodeName.MARKET_ANALYST_SUBGRAPH_EXECUTER, EdgeType.EDGE, [NodeName.MARKET_RESEARCH_MANAGER]),

            (NodeName.HEDGE_FUND_MANAGER, EdgeType.EDGE, [END]),
            # (NodeName.HEDGE_FUND_MANAGER, EdgeType.EDGE, [NodeName.REPORT_WRITER_AND_NOTIFIER]),
            # (NodeName.REPORT_WRITER_AND_NOTIFIER, EdgeType.CONDITIONAL_EDGE, [NodeName.REPORT_WRITER_AND_NOTIFIER_TOOLS, END]),
            # (NodeName.REPORT_WRITER_AND_NOTIFIER_TOOLS, EdgeType.EDGE, [END]),
        ]

    def _create_models(self):
        models_lists = [
            ModelWrapper(model=Model.GPT_4O_MINI, name=NodeName.MARKET_RESEARCH_MANAGER, schema=ManagerDecision),
            ModelWrapper(model=Model.GPT_4O, name=NodeName.HEDGE_FUND_MANAGER, schema=InvestmentDecision),
            # ModelWrapper(model=Model.GPT_4O_MINI, name=NodeName.REPORT_WRITER_AND_NOTIFIER, tools=self.other_tools),
        ]
        self.model_mapping = {model.name: model for model in models_lists}







