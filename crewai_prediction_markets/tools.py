"""Prediction-market tools for CrewAI agents.

Each tool wraps one verified endpoint of the public SimpleFunctions API.
No auth, no rate limit, no API key required. Tools are usable both inside
a CrewAI agent and standalone (call ``tool._run(...)`` directly).
"""

from __future__ import annotations

import json
from typing import Any, Optional

import requests

BASE = "https://simplefunctions.dev"
DEFAULT_TIMEOUT = 15


class _BaseSFTool:
    """Base tool with SF API access. Works standalone without crewai installed."""

    name: str = ""
    description: str = ""

    def _sf_get(self, path: str, params: Optional[dict] = None) -> Any:
        r = requests.get(f"{BASE}{path}", params=params, timeout=DEFAULT_TIMEOUT)
        r.raise_for_status()
        ct = r.headers.get("content-type", "")
        return r.json() if "json" in ct else r.text

    def _stringify(self, data: Any) -> str:
        return data if isinstance(data, str) else json.dumps(data)


# ── Tools ──────────────────────────────────────────────────


class GetContextTool(_BaseSFTool):
    name = "get_context"
    description = (
        "START HERE — single entry point that returns a global prediction-market "
        "snapshot bundle: top mispriced edges, 24h price movers, highlights, and "
        "traditional-market context. Read-only, no auth. Use this first when the "
        "user asks 'what's happening in markets right now'. Use the more specific "
        "tools only if the user wants one slice in isolation."
    )

    def _run(self) -> Any:
        return self._sf_get("/api/public/context")

    def run(self) -> str:
        return self._stringify(self._run())


class GetWorldStateTool(_BaseSFTool):
    name = "get_world_state"
    description = (
        "Get the calibrated world model: ~9,700 prediction markets distilled into "
        "~800 tokens of real-money probabilities across geopolitics, economics, "
        "tech, and policy. Use 'markdown' (default) for human/LLM-readable output, "
        "or 'json' for programmatic parsing. Use GetWorldChangesTool for cheap "
        "polling, or GetContextTool for the broader bundle."
    )

    def _run(self, format: str = "markdown") -> Any:
        return self._sf_get("/api/agent/world", {"format": format})

    def run(self, format: str = "markdown") -> str:
        return self._stringify(self._run(format))


class GetWorldChangesTool(_BaseSFTool):
    name = "get_world_changes"
    description = (
        "Get the incremental world-model delta since a given time — only the "
        "markets whose probability moved. ~30-50 tokens vs ~800 for the full state. "
        "'since' accepts a relative duration ('30m', '1h', '6h', '24h') or an "
        "ISO-8601 timestamp. Use for cheap polling loops; use GetWorldStateTool "
        "for an absolute snapshot."
    )

    def _run(self, since: Optional[str] = None) -> Any:
        params: dict = {"format": "markdown"}
        if since:
            params["since"] = since
        return self._sf_get("/api/agent/world/delta", params)

    def run(self, since: Optional[str] = None) -> str:
        return self._stringify(self._run(since))


class GetMarketEdgesTool(_BaseSFTool):
    name = "get_market_edges"
    description = (
        "Get currently actionable mispricings — markets where SimpleFunctions' "
        "causal model disagrees with the market price. Returns an array of edges "
        "with ticker, venue, prices, executableEdge in cents, confidence, "
        "liquidity, reasoning, age, and absorption. Use after GetContextTool if "
        "the user wants the raw edge list without bundled context."
    )

    def _run(self) -> Any:
        return self._sf_get("/api/edges")

    def run(self) -> str:
        return self._stringify(self._run())


class GetUncertaintyIndexTool(_BaseSFTool):
    name = "get_uncertainty_index"
    description = (
        "Get the four-signal prediction-market uncertainty index: uncertainty "
        "(0-100), geopolitical risk (0-100), momentum (-1 to +1), activity (0-100). "
        "Derived from real-money orderbook spreads across 30,000+ markets. Use "
        "when you need a single numeric pulse; use GetContextTool for the full "
        "bundle."
    )

    def _run(self) -> Any:
        return self._sf_get("/api/public/index")

    def run(self) -> str:
        return self._stringify(self._run())


class GetIdeasTool(_BaseSFTool):
    name = "get_ideas"
    description = (
        "Get LLM-generated, ready-to-act trade ideas derived from current edges, "
        "market changes, and source highlights. Each idea includes headline, pitch, "
        "conviction (high/medium/low), direction (buy_yes/buy_no), target market(s) "
        "with current price, catalyst, time horizon, and risk. Cached server-side "
        "(~12h). Use for pre-packaged actionable suggestions; use "
        "GetMarketEdgesTool for raw mispricings without LLM commentary."
    )

    def _run(self) -> Any:
        return self._sf_get("/api/public/ideas")

    def run(self) -> str:
        return self._stringify(self._run())
