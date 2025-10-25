import asyncio
import os
from datetime import datetime

from dotenv import load_dotenv

import market_analyst_graph.state
from agentic_stock_analyzer_graph import GraphManager as AgenticStockAnalyzerGraph
from stocks_market_recommender_graph import GraphManager as StocksMarketRecommenderGraph
from market_analyst_graph import GraphManager as MarketAnalystGraph

load_dotenv(override=True)

async def run_stocks_market_recommender():
    # company = "Apple Inc."
    # query = f"find historical prices for analysis of {company} stock"
    company = "Microsoft"
    query = f"Create a comprehensive analysis of {company}'s financial health using their latest quarterly financial statements."
    graph = MarketAnalystGraph()

    await graph.setup()
    result = await graph.run_graph(query=query)
    await graph.cleanup()

async def run_stocks_market_recommender_2():
    query = "Get historical price data for Microsoft (MSFT) over the past year."
    graph = MarketAnalystGraph()

    await graph.setup()
    result = await graph.run_graph(query=query)
    await graph.cleanup()

async def run_agentic_stocks_analyzer():
    company = "Microsoft"
    query = f"Should I invest in {company}? Today is {datetime.today().strftime('%m/%d/%Y')}"
    graph = AgenticStockAnalyzerGraph()

    await graph.setup()
    result = await graph.run_graph(query=query)
    print(f"result of graph: {result}")
    await graph.cleanup()

if __name__ == "__main__":
    # asyncio.run(run_stocks_market_recommender())
    asyncio.run(run_agentic_stocks_analyzer())
    # asyncio.run(run_stocks_market_recommender_2())