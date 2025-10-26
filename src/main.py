import asyncio
from datetime import datetime
from dotenv import load_dotenv
from agentic_stock_analyzer_graph import GraphManager as AgenticStockAnalyzerGraph
from market_analyst_graph import GraphManager as MarketAnalystGraph

load_dotenv(override=True)

async def run_stocks_market_recommender(query_str:str) -> None:
    graph = MarketAnalystGraph()
    await graph.setup()
    result = await graph.run_graph(query=query_str)
    await graph.cleanup()

async def run_agentic_stocks_analyzer(query_str: str, company: str) -> None:
    graph = AgenticStockAnalyzerGraph()
    await graph.setup()
    result = await graph.run_graph(query=query_str, company=company)
    await graph.cleanup()

if __name__ == "__main__":
    company = "Berkshire Hathaway"
    query = f"Should I invest in {company}? Today is {datetime.today().strftime('%m/%d/%Y')}"
    asyncio.run(run_agentic_stocks_analyzer(query_str=query, company=company))

    # query1 = f"Create a comprehensive analysis of Microsoft's financial health using their latest quarterly financial statements."
    # query2 = "Get historical price data for Microsoft (MSFT) over the past year."
    # asyncio.run(run_stocks_market_recommender(query1))