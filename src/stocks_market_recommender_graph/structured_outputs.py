from pydantic import BaseModel, Field, ConfigDict
from typing import Any, Dict, List, Optional


class McpCall(BaseModel):
    model_config = ConfigDict(extra='forbid')
    function_name: str = Field(..., description="The name of the MCP function called.")
    args: Optional[Dict[str, str]] = Field({}, description="Arguments passed to the MCP function.")
    result: str = Field(..., description="The raw result returned from MCP.")
    error: Optional[str] = Field(None, description="Error message if the call failed (leave null if success).")

class AnalysisOutput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    input_question: str = Field(..., description="The input question to the agent")
    technical_report: str = Field(
        description="Final synthesized professional summary report of all data returned from mcp calls (one or more)"
    )
    explanation: str = Field(
        description="Human-readable narrative explaining the findings in plain language."
    )
    calls: List[McpCall] = Field(
        description="All MCP calls executed (function + arguments + result)."
    )

class DecisionOutput(BaseModel):
    score: float = Field(
        description="Decision in [-1, 1]: -1=strong short, 0=flat, 1=strong long."
    )
    rationale: str = Field(
        description="Why this score? Reference key evidence from FinanceAgentOutput."
    )
    confidence: Optional[float] = Field(
        default=None, description="Optional confidence in [0,1]."
    )
    risks: Optional[str] = Field(
        default=None, description="Key risks, what could invalidate the stance, liquidity concerns."
    )

class QueryItem(BaseModel):
    query: str = Field(..., description="Business question the manager asked.")
    rationale: Optional[str] = Field(
        None,
        description="Why this query was chosen."
    )
    analysis: Optional[AnalysisOutput] = Field(
        None,
        description="The market analyst's structured output answering this query."
    )

class ManagerReport(BaseModel):
    queries: List[QueryItem] = Field(
        ...,
        description="List of all queries with their individual rationales."
    )
    decision_handoff: Optional[str] = Field(
        None,
        description="When and why the manager stopped querying and handed off to hedge_fund_manager."
    )
    decision: Optional[DecisionOutput] = Field(
        None, description="The hedge fund manager’s final decision, if available."
    )