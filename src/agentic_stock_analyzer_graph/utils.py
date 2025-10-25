from enum import Enum


class NodeName(str, Enum):
    MARKET_RESEARCH_MANAGER = "market_research_manager"
    MARKET_ANALYST_SUBGRAPH_EXECUTER = "market_analyst_subgraph_executor"
    HEDGE_FUND_MANAGER = "hedge_fund_manager"
    REPORT_WRITER_AND_NOTIFIER = "report_writer_and_notifier"
    REPORT_WRITER_AND_NOTIFIER_TOOLS = "report_writer_and_notifier_tools"