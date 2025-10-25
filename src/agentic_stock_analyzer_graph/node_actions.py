import asyncio
import json
from langchain_core.messages import AIMessage, SystemMessage, BaseMessage, HumanMessage
from typing import Any, Dict, List, Optional

from messages import ControlMessage

from market_analyst_graph import GraphManager as MarketAnalystGraph
from .prompts import market_research_manager_system_message, hedge_fund_manager_system_message
from .state import State, Phase
from .structured_outputs import QueryRequest, FinalQueryResult, McpQueryResult
from market_analyst_graph.structured_outputs import AnalysisOutput

MAX_INPUT_CHARS_PER_RESULT_IN_FINAL_DECISION = 1500

def _build_messages_for_market_research_manager(query_results: List[FinalQueryResult]) -> List[BaseMessage]:
    res = []
    for query_result in query_results:
        for mcp_query_result in query_result.mcp_query_results:
            res.append(AIMessage(content=f"you query: {mcp_query_result.query}, got response: {mcp_query_result.result}"))
    return res

async def _run_market_analyst_subgraph(query: str) -> Optional[AnalysisOutput]:
    graph = MarketAnalystGraph()
    await graph.setup()
    result = await graph.run_graph(query=query)
    await graph.cleanup()
    return result["results"] if result["results"] else None


def _construct_final_query_report(
    query_requests: List[QueryRequest],
    all_reports: List[AnalysisOutput],
) -> FinalQueryResult:
    """
    Construct a FinalQueryResult from aligned lists of QueryRequest and AnalysisOutput.
    Each index i in the lists corresponds to one query-answer pair.
    """
    return FinalQueryResult(
        mcp_query_results=[
            McpQueryResult(query=q, result=r)
            for q, r in zip(query_requests, all_reports)
        ],
    )


async def market_research_manager(state: State) -> Dict[str, Any]:
    system_message = market_research_manager_system_message
    additional_messages = [HumanMessage(content=state["human_question"])]
    if len(state["analyst_query_results"]) > 0:
        additional_messages = additional_messages + _build_messages_for_market_research_manager(state["analyst_query_results"])
    market_research_manager_messages = [SystemMessage(content=system_message)] + additional_messages
    # Invoke the func-injected LLM
    response = await market_research_manager.__model__.ainvoke(market_research_manager_messages)
    if response.action == "QUERY":
        num_of_queries = len(response.query_requests) if response.query_requests else 0
        if num_of_queries == 0:
            assert "market research manager didn't have any queries"
        # send a message with the queries to be executed by the subgraph executer node
        return {
            "messages": [AIMessage(content = f"market research manager decided to query {num_of_queries} queries")],
            "analysis_phase": Phase.QUERY,
            "queries": [response.query_requests if response.query_requests else []]
        }
    else:   # response.action = "FINAL"
        return {
            "messages": [AIMessage(content = f"market research manager decided to finish queryin and move to decision")],
            "analysis_phase": Phase.DECIDE,
            "decision_handoff": response.decision_handoff,
        }

def _clamp_text(s: str, limit=MAX_INPUT_CHARS_PER_RESULT_IN_FINAL_DECISION) -> str:
    return s if len(s) <= limit else s[:limit] + "…[truncated]"

def _flatten_single_mcp_query_results(mcp_query_result: McpQueryResult) -> str:
    ai_query_text = mcp_query_result.query.query
    ai_query_rational = mcp_query_result.query.rationale
    analysis_report = mcp_query_result.result
    input_question = analysis_report.input_question
    technical_report = analysis_report.technical_report
    explanation = analysis_report.explanation
    mcp_results = []
    for call in analysis_report.calls:
        mcp_results.append((call.function_name, call.error if call.error else call.result))
    mcp_calls_str = ", ".join(f"function mcp: {q}, function (possibly concatenated) result: {_clamp_text(a)}\n" for q, a in mcp_results)
    return (f"ai agent query:{ai_query_text}\n"
            f"ai query rational:{ai_query_rational}\n"
            f"eventual question asked by subagent:{input_question}\n"
            f"technical report given after mcp call(s): {technical_report}\n"
            f"explanation of report: {explanation}\n"
            f"mcp proper calls: {mcp_calls_str}\n")

def _flatten_queries_and_results(results: List[FinalQueryResult]) -> str:
    res = []
    for final_query_result in results:
        for mcp_query_result in final_query_result.mcp_query_results:
            res.append(_flatten_single_mcp_query_results(mcp_query_result))

    return "\n".join(res)


async def hedge_fund_manager(state: State) -> Dict[str, Any]:
    system_message = hedge_fund_manager_system_message
    analyst_query_results = state["analyst_query_results"]
    decision_query_text = _flatten_queries_and_results(analyst_query_results)
    print(f"******decision={decision_query_text}******")
    user_message = HumanMessage(content="Please perform your investment analysis on the following data retrieved for you and return the required answer:\n" +
                    decision_query_text)

    hedge_fund_manager_messages = [SystemMessage(content=system_message)] + [user_message]
    # Invoke the func-injected LLM
    response = await hedge_fund_manager.__model__.ainvoke(hedge_fund_manager_messages)
    return {
        "messages": [AIMessage(content=response.model_dump_json())]
    }

async def market_analyst_subgraph_executer(state: State) -> Dict[str, Any]:
    query_requests = state["queries"][-1]
    # run subgraph per query
    subgraph_executions = [_run_market_analyst_subgraph(query_request.query) for query_request in query_requests]
    results = await asyncio.gather(*subgraph_executions)
    # merge results - each result is of type AnalysisOutput and construct FinalQueryResult
    query_results = _construct_final_query_report(query_requests, results)
    # Return updated state
    return {
        "messages": [ControlMessage(content="queries executed successfully by subgraph executer")],
        "analyst_query_results": [query_results],
    }
