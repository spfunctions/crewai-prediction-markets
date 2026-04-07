# crewai-prediction-markets

[![PyPI](https://img.shields.io/pypi/v/crewai-prediction-markets)](https://pypi.org/project/crewai-prediction-markets/)
[![Python](https://img.shields.io/pypi/pyversions/crewai-prediction-markets)](https://pypi.org/project/crewai-prediction-markets/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

CrewAI tools for **real-time prediction market data**. Drop-in tools that give any
CrewAI agent or crew world awareness from 30,000+ Kalshi and Polymarket contracts —
no auth required.

```python
from crewai import Agent, Crew, Task
from crewai_prediction_markets import prediction_market_tools

analyst = Agent(
    role="Market Analyst",
    goal="Identify the most actionable prediction-market edges right now",
    backstory="You read the world through prediction-market prices.",
    tools=prediction_market_tools(),
)

task = Task(
    description="What is the highest-conviction trade idea right now? Cite the ticker and the catalyst.",
    expected_output="One trade idea with ticker, conviction, current price, and catalyst.",
    agent=analyst,
)

crew = Crew(agents=[analyst], tasks=[task])
print(crew.kickoff())
```

---

## Install

```bash
pip install crewai-prediction-markets
```

Only depends on `requests`. CrewAI itself is **not** a hard dependency — you can
use the tools standalone (see the [Standalone usage](#standalone-no-crewai-needed)
section below).

## Tools

All six tools hit the public SimpleFunctions API. **No API key, no rate limit, no
auth.** Every endpoint below is verified live.

| Tool | Endpoint | When to use |
|------|----------|-------------|
| `GetContextTool` | `/api/public/context` | **Start here.** Single bundle: edges, movers, highlights, traditional-market context. |
| `GetWorldStateTool` | `/api/agent/world` | ~800-token compressed snapshot of all markets, ideal for system-prompt injection. |
| `GetWorldChangesTool` | `/api/agent/world/delta` | ~30-50 token incremental delta — cheap polling loops. |
| `GetMarketEdgesTool` | `/api/edges` | Raw mispricings (thesis price vs market price) with reasoning. |
| `GetUncertaintyIndexTool` | `/api/public/index` | Single numeric pulse: uncertainty, geopolitical risk, momentum, activity. |
| `GetIdeasTool` | `/api/public/ideas` | LLM-generated trade ideas with conviction, catalyst, time horizon. |

## Multi-agent crew example

```python
from crewai import Agent, Crew, Task, Process
from crewai_prediction_markets import prediction_market_tools

scout = Agent(
    role="Market Scout",
    goal="Surface the top 3 mispriced edges across Kalshi and Polymarket",
    tools=prediction_market_tools(),
)

writer = Agent(
    role="Note Writer",
    goal="Turn raw edges into a concise daily note for a portfolio manager",
    backstory="You write tight, opinionated, 200-word market notes.",
)

scout_task = Task(
    description="Find the 3 highest-conviction edges with catalysts in the next 7 days",
    expected_output="Bullet list of 3 edges with ticker, executableEdge, catalyst, time horizon",
    agent=scout,
)

write_task = Task(
    description="Write a 200-word daily note covering the 3 edges",
    expected_output="A 200-word markdown note",
    agent=writer,
    context=[scout_task],
)

crew = Crew(agents=[scout, writer], tasks=[scout_task, write_task], process=Process.sequential)
print(crew.kickoff())
```

## Standalone (no crewai needed)

Every tool exposes both a `_run` (returning the parsed payload) and a `run`
(returning a JSON string ready for an LLM tool message). Use whichever fits
your loop:

```python
from crewai_prediction_markets import GetUncertaintyIndexTool, GetIdeasTool

idx = GetUncertaintyIndexTool()._run()
print(f"Uncertainty: {idx['uncertainty']}/100")

ideas = GetIdeasTool()._run()
top = ideas["ideas"][0]
print(f"Top idea: {top['headline']} ({top['conviction']} conviction)")
```

## Response shapes

### `GetContextTool` → dict
```python
{
  "edges": [...],            # top mispricings
  "movers": [...],           # 24h price movers
  "highlights": [...],       # recent narrative-shaping events
  "traditionalMarkets": {...}
}
```

### `GetUncertaintyIndexTool` → dict
```python
{
  "uncertainty": 22,          # 0-100
  "geopolitical": 0,          # 0-100
  "momentum": -0.08,          # -1 to +1
  "activity": 99,             # 0-100
  "components": {...},
  "timestamp": "2026-04-07T07:18:03.451Z",
}
```

### `GetMarketEdgesTool` → dict
```python
{
  "edges": [
    {
      "ticker": "KXFEDDECISION-25DEC",
      "venue": "kalshi",
      "title": "Will the Fed cut rates in December?",
      "marketPrice": 42,           # cents
      "thesisPrice": 31,           # cents
      "executableEdge": 11,        # cents (after spread)
      "confidence": 0.78,
      "liquidityScore": "high",
      "direction": "no",
      "reasoning": "...",
    },
    ...
  ]
}
```

### `GetIdeasTool` → dict
```python
{
  "generatedAt": "2026-04-07T01:29:41Z",
  "cached": True,
  "ideas": [
    {
      "headline": "...",
      "pitch": "...",
      "conviction": "high",
      "direction": "buy_yes",
      "markets": [{"url": "...", "ticker": "...", "currentPrice": 14.5, "venue": "polymarket"}],
      "catalyst": "...",
      "timeHorizon": "2w",
      "risk": "...",
    },
    ...
  ]
}
```

## Errors

Tools call `requests.Response.raise_for_status()` on every response, so any
non-2xx surfaces as a `requests.HTTPError`. Wrap in `try/except` if your crew
should degrade gracefully:

```python
import requests
from crewai_prediction_markets import GetContextTool

try:
    ctx = GetContextTool()._run()
except requests.HTTPError as e:
    ctx = {"error": str(e), "edges": [], "movers": []}
```

## Sister packages

If you're not using CrewAI, use the wrapper for your stack:

| Stack | Package |
|-------|---------|
| Vercel AI SDK | [`vercel-ai-prediction-markets`](https://github.com/spfunctions/vercel-ai-prediction-markets) |
| LangChain / LangGraph | [`langchain-prediction-markets`](https://github.com/spfunctions/langchain-prediction-markets) |
| OpenAI Agents SDK / function calling | [`openai-agents-prediction-markets`](https://github.com/spfunctions/openai-agents-prediction-markets) |
| MCP / Claude / Cursor | [`simplefunctions-cli`](https://github.com/spfunctions/simplefunctions-cli) |
| Bare Python SDK | [`simplefunctions-python`](https://github.com/spfunctions/simplefunctions-python) |

## Testing

```bash
pip install -e .[dev]
pytest
```

11 tests, all `requests.get`-mocked — no network required.

## License

MIT — built by [SimpleFunctions](https://simplefunctions.dev).
