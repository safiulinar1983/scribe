#!/usr/bin/env python3
from __future__ import annotations
import argparse, pathlib, yaml
from core.llm import OllamaProvider
from core.agent import Agent
from core.skill_loader import SkillLoader
from core.tools import ToolRegistry, Tool
from core.conversation import ConversationManager
from memory.manager import MemoryManager
from tools.registry import register_macos
from tools.notes_importer import NotesImporter

def load_config(root):
    return yaml.safe_load((root/'config.yaml').read_text(encoding='utf-8'))

def main():
    root=pathlib.Path(__file__).resolve().parent
    cfg=load_config(root)
    memory=MemoryManager(root/cfg['memory']['database'])
    importer=NotesImporter(memory)
    ap=argparse.ArgumentParser()
    ap.add_argument('--import-notes',action='store_true')
    args=ap.parse_args()
    if args.import_notes:
        print('Индексирую Apple Notes (только чтение)...')
        print(importer.sync())
        return
    registry=ToolRegistry(); register_macos(registry)
    S=lambda p,req=[]:{'type':'object','properties':p,'required':req}
    registry.register(Tool('memory.search','Найти релевантные записи Long-term Memory.',S({'query':{'type':'string'},'limit':{'type':'integer'}},['query']),lambda query,limit=10: memory.search(query,limit)))
    registry.register(Tool('memory.remember','Сохранить долговременный факт по явной просьбе пользователя.',S({'content':{'type':'string'},'category':{'type':'string'},'importance':{'type':'integer'}},['content']),lambda content,category='other',importance=5: memory.remember(content,category=category,source='user',importance=importance)))
    registry.register(Tool('memory.list','Показать последние записи памяти.',S({'limit':{'type':'integer'}}),lambda limit=50: memory.list(limit)))
    provider=OllamaProvider(cfg['llm']['base_url'],cfg['llm']['model'],cfg['llm']['temperature'],cfg['llm']['timeout'])
    agent=Agent(provider,registry,SkillLoader(root/cfg['skills']['directory']),ConversationManager(root/cfg['memory']['conversations_database']),memory)
    print('Scribe — локальный AI-агент. Qwen3 14B / Ollama.')
    print('Команды: /help, /memory, /import-notes, /quit')
    while True:
        try: text=input('\n> ').strip()
        except (EOFError,KeyboardInterrupt): print(); break
        if not text: continue
        if text in ('/quit','/exit'): break
        if text=='/help':
            print('Например: «Поставь завтра в 9:30 бассейн на час», «Создай напоминание…», «Запомни, что…»'); continue
        if text=='/memory':
            for x in memory.list(): print(f"#{x['id']} [{x['category']}] {x['content']}")
            continue
        if text=='/import-notes': print(importer.sync()); continue
        try: print('\n'+agent.handle(text))
        except Exception as e: print(f'Ошибка: {e}')

if __name__=='__main__': main()
