import asyncio
import os
from dotenv import load_dotenv
from stocks_market_recommender_graph import GraphManager

load_dotenv(override=True)

async def run_stock_analyzer():
    # company = "Apple Inc."
    # query = f"find historical prices for analysis of {company} stock"
    company = "Microsoft"
    query = f"Create a comprehensive analysis of {company}'s financial health using their latest quarterly financial statements."
    graph = GraphManager()

    await graph.setup()
    result = await graph.run_graph(query=query)
    await graph.cleanup()

if __name__ == "__main__":
    asyncio.run(run_stock_analyzer())