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
