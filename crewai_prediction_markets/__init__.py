from crewai_prediction_markets.tools import (
    GetWorldStateTool,
    GetUncertaintyIndexTool,
    GetMarketEdgesTool,
    GetMarketDetailTool,
)

def prediction_market_tools():
    return [GetWorldStateTool(), GetUncertaintyIndexTool(), GetMarketEdgesTool(), GetMarketDetailTool()]

__all__ = [
    "GetWorldStateTool", "GetUncertaintyIndexTool",
    "GetMarketEdgesTool", "GetMarketDetailTool",
    "prediction_market_tools",
]
