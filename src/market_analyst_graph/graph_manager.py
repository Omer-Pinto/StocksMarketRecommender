from enum import Enum

from graph import GraphWrapper, NodeWrapper, ToolNodeWrapper, EdgeType
from langgraph.constants import START, END
from models import ModelWrapper, Model

from .state import State
from .structured_outputs import AnalysisOutput
from .tools_setup import tools_setup, tools_cleanup
from .node_actions import market_analyst, mcp_calls_summarizer
from .routers import market_analyst_router
from .utils import NodeName

class GraphManager:
    def __init__(self):
        self.tool_wrappers = None
        self.mcp_tools = None
        self.other_tools = None
        self.graph = None
        self.node_wrappers = None
        self.model_mapping = None
        self.graph_wrapper = None
    
    def get_graph_drawing(self):
        return self.graph_wrapper.get_graph_drawing()

    async def setup(self):
        self.tool_wrappers = await tools_setup()
        self.mcp_tools = [
            tool
            for wrapper in self.tool_wrappers
            if wrapper.name == "yahoo_finance_mcp"
            for tool in wrapper.tools
        ]
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
            state_type=State,
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
            "messages": [{"role": "user", "content": query}],
            "mcp_tools_used": [],
        }
        result = await self.graph_wrapper.run_superstep(initial_state=state)
        return result

    def _create_nodes(self):
        self.node_wrappers = [
            NodeWrapper(name=NodeName.MARKET_ANALYST, action=market_analyst, model_wrapper=self.model_mapping.get(NodeName.MARKET_ANALYST),
                        router=market_analyst_router),
            ToolNodeWrapper(name=NodeName.MARKET_ANALYST_TOOLS, tools=self.mcp_tools),
            NodeWrapper(name=NodeName.MCP_CALLS_SUMMARIZER, action=mcp_calls_summarizer, model_wrapper=self.model_mapping.get(NodeName.MCP_CALLS_SUMMARIZER)),
        ]

    def _create_edges(self):
        self.edges_info = [
            (START, EdgeType.EDGE, [NodeName.MARKET_ANALYST]),
            (NodeName.MARKET_ANALYST, EdgeType.CONDITIONAL_EDGE, [NodeName.MARKET_ANALYST_TOOLS, NodeName.MCP_CALLS_SUMMARIZER]),
            (NodeName.MARKET_ANALYST_TOOLS, EdgeType.EDGE, [NodeName.MARKET_ANALYST]),
            (NodeName.MCP_CALLS_SUMMARIZER, EdgeType.EDGE, [END]),
        ]

    def _create_models(self):
        models_lists = [
            ModelWrapper(model=Model.GPT_4O, name=NodeName.MARKET_ANALYST, tools=self.mcp_tools, temperature=1.0),
            ModelWrapper(model=Model.GPT_4O_MINI, name=NodeName.MCP_CALLS_SUMMARIZER, schema=AnalysisOutput, temperature=1.0),
        ]
        self.model_mapping = {model.name: model for model in models_lists}







