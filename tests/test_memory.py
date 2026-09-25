import tempfile
from pathlib import Path
from memory.manager import MemoryManager

def test_memory_roundtrip():
    with tempfile.TemporaryDirectory() as d:
        m=MemoryManager(Path(d)/'memory.db')
        x=m.remember('Scribe uses Qwen3 14B',source='user')
        assert x['id']
        assert m.search('Qwen3 14B')[0]['content']=='Scribe uses Qwen3 14B'
