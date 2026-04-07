"""Tests for crewai-prediction-markets — all `requests` calls are mocked,
so the suite runs offline in CI without hitting the live SimpleFunctions API."""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from crewai_prediction_markets import (
    GetContextTool,
    GetWorldStateTool,
    GetWorldChangesTool,
    GetMarketEdgesTool,
    GetUncertaintyIndexTool,
    GetIdeasTool,
    prediction_market_tools,
)


# ── Helpers ───────────────────────────────────────────────


def _mock_response(body: Any, content_type: str = "application/json", status: int = 200) -> MagicMock:
    resp = MagicMock()
    resp.status_code = status
    resp.headers = {"content-type": content_type}
    if isinstance(body, str):
        resp.text = body
    else:
        resp.text = json.dumps(body)
    resp.json = MagicMock(return_value=body)
    resp.raise_for_status = MagicMock(return_value=None)
    return resp


# ── Bundle shape ──────────────────────────────────────────


def test_prediction_market_tools_exports_six_in_stable_order():
    tools = prediction_market_tools()
    assert len(tools) == 6
    assert [t.name for t in tools] == [
        "get_context",
        "get_world_state",
        "get_world_changes",
        "get_market_edges",
        "get_uncertainty_index",
        "get_ideas",
    ]


def test_every_tool_has_a_description():
    for t in prediction_market_tools():
        assert t.description and len(t.description) > 20


# ── Per-tool URL + behavior ──────────────────────────────


@patch("crewai_prediction_markets.tools.requests.get")
def test_get_context_hits_context_endpoint(mock_get: MagicMock):
    mock_get.return_value = _mock_response({"edges": [], "movers": []})
    out = GetContextTool().run()
    mock_get.assert_called_once()
    assert mock_get.call_args.args[0] == "https://simplefunctions.dev/api/public/context"
    assert json.loads(out) == {"edges": [], "movers": []}


@patch("crewai_prediction_markets.tools.requests.get")
def test_get_world_state_defaults_to_markdown(mock_get: MagicMock):
    mock_get.return_value = _mock_response("# State", content_type="text/markdown")
    out = GetWorldStateTool().run()
    assert mock_get.call_args.kwargs["params"] == {"format": "markdown"}
    assert out == "# State"


@patch("crewai_prediction_markets.tools.requests.get")
def test_get_world_state_passes_json_format(mock_get: MagicMock):
    mock_get.return_value = _mock_response({"regime": "neutral"})
    out = GetWorldStateTool().run(format="json")
    assert mock_get.call_args.kwargs["params"] == {"format": "json"}
    assert json.loads(out) == {"regime": "neutral"}


@patch("crewai_prediction_markets.tools.requests.get")
def test_get_world_changes_no_since(mock_get: MagicMock):
    mock_get.return_value = _mock_response("# Delta", content_type="text/markdown")
    GetWorldChangesTool().run()
    assert mock_get.call_args.kwargs["params"] == {"format": "markdown"}


@patch("crewai_prediction_markets.tools.requests.get")
def test_get_world_changes_with_since(mock_get: MagicMock):
    mock_get.return_value = _mock_response("# Delta", content_type="text/markdown")
    GetWorldChangesTool().run(since="6h")
    assert mock_get.call_args.kwargs["params"] == {"format": "markdown", "since": "6h"}


@patch("crewai_prediction_markets.tools.requests.get")
def test_get_market_edges(mock_get: MagicMock):
    mock_get.return_value = _mock_response({"edges": [{"ticker": "KX", "executableEdge": 12}]})
    out = GetMarketEdgesTool().run()
    assert mock_get.call_args.args[0] == "https://simplefunctions.dev/api/edges"
    assert json.loads(out)["edges"][0]["ticker"] == "KX"


@patch("crewai_prediction_markets.tools.requests.get")
def test_get_uncertainty_index_returns_index_shape(mock_get: MagicMock):
    payload = {"uncertainty": 22, "geopolitical": 0, "momentum": -0.08, "activity": 99}
    mock_get.return_value = _mock_response(payload)
    out = GetUncertaintyIndexTool().run()
    assert mock_get.call_args.args[0] == "https://simplefunctions.dev/api/public/index"
    data = json.loads(out)
    assert data["uncertainty"] == 22 and data["activity"] == 99


@patch("crewai_prediction_markets.tools.requests.get")
def test_get_ideas(mock_get: MagicMock):
    mock_get.return_value = _mock_response(
        {"ideas": [{"headline": "h", "conviction": "high"}]}
    )
    out = GetIdeasTool().run()
    assert mock_get.call_args.args[0] == "https://simplefunctions.dev/api/public/ideas"
    assert json.loads(out)["ideas"][0]["conviction"] == "high"


# ── Error handling ────────────────────────────────────────


@patch("crewai_prediction_markets.tools.requests.get")
def test_raise_for_status_propagates(mock_get: MagicMock):
    import requests as r

    err_resp = MagicMock()
    err_resp.raise_for_status = MagicMock(side_effect=r.HTTPError("404"))
    mock_get.return_value = err_resp
    with pytest.raises(r.HTTPError):
        GetContextTool().run()
