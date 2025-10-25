from pydantic import BaseModel, Field, ConfigDict
from typing import Any, Dict, List, Optional, Literal

from market_analyst_graph.structured_outputs import AnalysisOutput


class InvestmentDecision(BaseModel):
    score: float = Field(
        description="Score that represents an investment suggestion - any float in range [-1, 1]: "
                    "- 1 = strong short, 0 = flat(no suggested position), 1 = strong long."
    )
    rationale: str = Field(
        description="Provide a rationale to your scoring decision. Reference key evidence from your input."
    )
    summary: str = Field(
        description="A textual description to accompany your numerical score"
    )
    confidence: Optional[float] = Field(
        default=None, description="Optionally supply your confidence in the score you gave - should be any float in [0,1] range."
    )
    risks: Optional[str] = Field(
        default=None, description="Optional Key risks that could invalidate the your investment decision."
    )


class QueryRequest(BaseModel):
    query: str = Field(..., description="Market question related to the stock at hand, the manager asked.")
    rationale: Optional[str] = Field(None, description="Why this query was chosen.")

class ManagerDecision(BaseModel):
    action: Literal["QUERY", "FINAL"] = Field(..., description="What the manager wants to do next - perform more financial "
                                                               "queries or continue to the hedge manager for investment decision.")
    query_requests: Optional[List[QueryRequest]] = Field(None, description="If action=QUERY, the actual query request the manager would like to ask the analyst")
    decision_handoff: Optional[str] = Field(None, description="If action=FINAL, why the manager stopped querying and handed off to hedge_fund_manager.")

class McpQueryResult(BaseModel):
    query: QueryRequest = Field(..., description="The query data the manager asked analyst")
    result: AnalysisOutput = Field(..., description="The analysis output from financial query")

class FinalQueryResult(BaseModel):
    mcp_query_results: List[McpQueryResult] = Field(...,  description="The mcp query results for all queries")