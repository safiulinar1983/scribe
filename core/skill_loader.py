from pathlib import Path


class SkillLoader:
    def __init__(self, directory: str | Path): self.directory = Path(directory)
    def load(self) -> dict[str, str]:
        out = {}
        if self.directory.exists():
            for p in sorted(self.directory.glob('*.md')):
                out[p.stem] = p.read_text(encoding='utf-8')
        return out
    def combined_prompt(self) -> str:
        skills = self.load()
        if not skills: return ''
        return '\n\n'.join(f"===== SKILL: {k} =====\n{v}" for k,v in skills.items())
