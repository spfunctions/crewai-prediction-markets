from crewai_prediction_markets import GetWorldStateTool, GetUncertaintyIndexTool, prediction_market_tools

def test_world_state_tool():
    tool = GetWorldStateTool()
    assert tool.name == "get_world_state"

def test_index_tool_live():
    tool = GetUncertaintyIndexTool()
    result = tool._run()
    assert 0 <= result["uncertainty"] <= 100

def test_prediction_market_tools():
    tools = prediction_market_tools()
    assert len(tools) == 4
