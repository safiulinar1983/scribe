from core.tools import Tool,ToolRegistry

def test_whitelist():
    r=ToolRegistry(); r.register(Tool('x','x',{'type':'object'},lambda:'ok'))
    assert r.get('x') is not None
    assert r.get('shell') is None
