# Scribe

Локальный персональный AI-агент для macOS.

Первый рабочий прототип рассчитан на **MacBook Air M4 16 GB** и использует только **Qwen3 14B через Ollama**.

## Быстрый старт

```bash
cd ~/scribe
./setup.sh
ollama pull qwen3:14b
./run.sh
```

Проверка Notes-импорта:

```bash
./run.sh --import-notes
```

## Что реализовано в первой версии

- модульный `LLMProvider` с Ollama;
- Qwen3 14B в конфигурации;
- Agent Core;
- Markdown Skill Loader;
- whitelist Tool Registry;
- SQLite MemoryManager с WAL, миграциями и транзакциями;
- отдельная Conversation History;
- явная команда `Запомни, что...`;
- macOS Calendar/Reminders/Notes через `osascript`;
- NotesImporter: первичный read-only импорт и синхронизация по hash/modified date;
- подтверждение опасных удалений в CLI;
- резервная копия перед полной очисткой Memory;
- переносимые относительные пути;
- `setup.sh` и `run.sh`.

## Важно

Scribe не предоставляет LLM произвольный shell/Python/SQL/файловый доступ. Все системные действия проходят через зарегистрированные Tools и их валидацию.

Ollama и модель являются внешней системной зависимостью и не копируются в каталог проекта.
