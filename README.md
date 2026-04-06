# crewai-prediction-markets

CrewAI tools for prediction market data. Give your AI crew real-time world awareness from 30,000+ markets.

```bash
pip install crewai-prediction-markets
```

```python
from crewai import Agent, Crew, Task
from crewai_prediction_markets import prediction_market_tools

analyst = Agent(
    role='Market Analyst',
    goal='Analyze prediction market data to identify risks and opportunities',
    tools=prediction_market_tools(),
)

task = Task(
    description='What are the key geopolitical risks right now?',
    agent=analyst,
)

crew = Crew(agents=[analyst], tasks=[task])
result = crew.kickoff()
```

## Tools
| Tool | Description |
|------|-------------|
| `GetWorldStateTool` | Full prediction market world state |
| `GetUncertaintyIndexTool` | Four-signal uncertainty index |
| `GetMarketEdgesTool` | Actionable mispricings |
| `GetMarketDetailTool` | Single market with orderbook |

## Standalone (no crewai needed)
```python
from crewai_prediction_markets import GetUncertaintyIndexTool
tool = GetUncertaintyIndexTool()
data = tool._run()
print(f"Uncertainty: {data['uncertainty']}/100")
```

## License
MIT — [SimpleFunctions](https://simplefunctions.dev)
