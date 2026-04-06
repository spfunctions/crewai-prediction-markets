import json
import requests

BASE = "https://simplefunctions.dev"

class _BaseSFTool:
    """Base tool with SF API access. Works standalone without crewai installed."""
    name: str = ""
    description: str = ""

    def _sf_get(self, path, params=None):
        r = requests.get(f"{BASE}{path}", params=params, timeout=15)
        r.raise_for_status()
        return r.json() if "json" in r.headers.get("content-type", "") else r.text

class GetWorldStateTool(_BaseSFTool):
    name = "get_world_state"
    description = "Get real-time prediction market world state from 30,000+ markets. Returns uncertainty index, regime summary, actionable edges, movers, and divergences."

    def _run(self, format="markdown"):
        return self._sf_get("/api/agent/world", {"format": format})

    def run(self, format="markdown"):
        result = self._run(format)
        return result if isinstance(result, str) else json.dumps(result)

class GetUncertaintyIndexTool(_BaseSFTool):
    name = "get_uncertainty_index"
    description = "Get the prediction market uncertainty index: uncertainty (0-100), geopolitical risk (0-100), momentum (-1 to +1), activity (0-100)."

    def _run(self):
        return self._sf_get("/api/public/index")

    def run(self):
        return json.dumps(self._run())

class GetMarketEdgesTool(_BaseSFTool):
    name = "get_market_edges"
    description = "Get actionable edges — markets where thesis-implied price diverges from market price. Includes reasoning, causal path, age, and absorption."

    def _run(self):
        return self._sf_get("/api/edges")

    def run(self):
        return json.dumps(self._run())

class GetMarketDetailTool(_BaseSFTool):
    name = "get_market_detail"
    description = "Get detailed data for a specific prediction market by ticker."

    def _run(self, ticker, depth=False):
        params = {}
        if depth:
            params["depth"] = "true"
        return self._sf_get(f"/api/public/market/{ticker}", params)

    def run(self, ticker, depth=False):
        return json.dumps(self._run(ticker, depth))
