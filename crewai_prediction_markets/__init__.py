from crewai_prediction_markets.tools import (
    GetContextTool,
    GetWorldStateTool,
    GetWorldChangesTool,
    GetMarketEdgesTool,
    GetUncertaintyIndexTool,
    GetIdeasTool,
)


def prediction_market_tools():
    """Return all six prediction-market tools as a list, in stable order."""
    return [
        GetContextTool(),
        GetWorldStateTool(),
        GetWorldChangesTool(),
        GetMarketEdgesTool(),
        GetUncertaintyIndexTool(),
        GetIdeasTool(),
    ]


__all__ = [
    "GetContextTool",
    "GetWorldStateTool",
    "GetWorldChangesTool",
    "GetMarketEdgesTool",
    "GetUncertaintyIndexTool",
    "GetIdeasTool",
    "prediction_market_tools",
]
