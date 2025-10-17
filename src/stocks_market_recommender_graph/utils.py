from enum import Enum


class NodeName(str, Enum):
    MARKET_ANALYST = "market_analyst"
    MARKET_ANALYST_TOOLS = "market_analyst_tools"
    MCP_CALLS_SUMMARIZER = "mcp_calls_summarizer"
    REPORT_FILE_WRITER = "report_file_writer"
    REPORT_FILE_WRITER_TOOLS = "report_file_writer_tools"