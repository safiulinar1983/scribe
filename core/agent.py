from __future__ import annotations
import json, re
from datetime import datetime
from .llm import LLMProvider
from .tools import ToolRegistry
from .skill_loader import SkillLoader
from .conversation import ConversationManager

SYSTEM = '''Ты Scribe — локальный персональный AI-агент пользователя на macOS.
Отвечай по-русски, если пользователь не просит другой язык.
Ты не имеешь произвольного доступа к shell, Python, SQL или файловой системе. Для системных действий используй только зарегистрированные Tools.
Не выдумывай результаты выполнения Tool.
Если действие опасное и требует подтверждения, сначала попроси пользователя подтвердить его.
Не сохраняй сообщения в Long-term Memory автоматически. Сохраняй память только когда пользователь явно просит «Запомни, что…» или эквивалентно.
'''

class Agent:
    def __init__(self, llm: LLMProvider, registry: ToolRegistry, skills: SkillLoader, conversations: ConversationManager, memory):
        self.llm=llm; self.registry=registry; self.skills=skills; self.conversations=conversations; self.memory=memory
        self.cid=self.conversations.new()
        self.pending_confirmation = None

    def _memory_command(self, text):
        m=re.match(r'^\s*запомни\s*,?\s*что\s+(.+)$', text, re.I|re.S)
        if not m: return None
        content=m.group(1).strip(); rec=self.memory.remember(content, source='user')
        return f"Запомнил: {rec['content']}"

    def handle(self, text):
        if self.pending_confirmation:
            answer = text.strip().lower().rstrip(".!?")
            if answer in {"да", "да, удалить", "подтверждаю", "подтвердить", "выполнить", "удалить"}:
                name, args = self.pending_confirmation
                self.pending_confirmation = None
                try:
                    result = self.registry.execute(name, args, confirmed=True)
                    reply = "Готово. Операция выполнена."
                except Exception as e:
                    reply = f"Не удалось выполнить операцию: {e}"
                self.conversations.add(self.cid, "user", text)
                self.conversations.add(self.cid, "assistant", reply)
                return reply
            if answer in {"нет", "отмена", "отменить", "не надо"}:
                self.pending_confirmation = None
                reply = "Операция отменена."
                self.conversations.add(self.cid, "user", text)
                self.conversations.add(self.cid, "assistant", reply)
                return reply

        direct=self._memory_command(text)
        if direct:
            self.conversations.add(self.cid,'user',text); self.conversations.add(self.cid,'assistant',direct); return direct
        self.conversations.add(self.cid,'user',text)
        mem=self.memory.search(text,limit=5)
        context='\n'.join(f"- {x['content']}" for x in mem)
        now = datetime.now().astimezone()
        date_context = (
            f"Текущая дата и время: {now.strftime('%Y-%m-%d %H:%M:%S %z')}."
            "\nПри работе с относительными датами («сегодня», «завтра», «послезавтра» и т.п.) обязательно считай их относительно этой даты."
        )
        sys = SYSTEM + "\n\n" + date_context + "\n\n" + self.skills.combined_prompt()
        if context: sys += '\n\nРелевантная Long-term Memory:\n'+context
        messages=[{'role':'system','content':sys},{'role':'user','content':text}]
        for _ in range(2):
            resp=self.llm.chat(messages,self.registry.definitions())
            if not resp.tool_calls:
                self.conversations.add(self.cid,'assistant',resp.content); return resp.content
            messages.append({'role':'assistant','content':resp.content,'tool_calls':resp.tool_calls})
            for call in resp.tool_calls:
                fn=call.get('function',{})
                name=fn.get('name'); args=fn.get('arguments') or {}
                if isinstance(args,str): args=json.loads(args)
                tool=self.registry.get(name)
                if not tool: result={'error':'unknown_tool'}
                elif tool.dangerous:

                    self.pending_confirmation = (name, args)
                    result={'error':'confirmation_required','message':f'Для {name} требуется подтверждение пользователя.'}
                else:
                    try: result={'ok':True,'result':self.registry.execute(name,args,confirmed=True)}
                    except Exception as e: result={'ok':False,'error':str(e)}
                messages.append({'role':'tool','content':json.dumps(result,ensure_ascii=False),'tool_call_id':call.get('id','')})
        return 'Не удалось завершить цепочку действий за допустимое число шагов.'
