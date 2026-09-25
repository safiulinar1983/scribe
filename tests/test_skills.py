from core.skill_loader import SkillLoader
from pathlib import Path

def test_load():
    s=SkillLoader(Path(__file__).parents[1]/'skills').load()
    assert 'calendar' in s
