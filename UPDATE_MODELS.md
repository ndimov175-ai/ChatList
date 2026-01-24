# Обновление моделей OpenRouter

Если вы получаете ошибки 404 для моделей OpenRouter, выполните следующие шаги:

## Способ 1: Обновить через интерфейс (рекомендуется)

1. Запустите приложение
2. Перейдите в **Tools → Manage Models**
3. Найдите модель с ошибкой (например, `meta-llama/llama-3-8b-instruct:free`)
4. Нажмите **Delete** для удаления неработающей модели
5. Нажмите **Add Model** для добавления новой:
   - **Model Name**: используйте актуальное имя из списка ниже
   - **API URL**: `https://openrouter.ai/api/v1/chat/completions`
   - **API Key Variable**: `OPENROUTER_API_KEY`

## Способ 2: Получить список доступных моделей

Запустите утилиту для получения актуального списка моделей:

```bash
python -m chatlist.utils.openrouter_models
```

Это создаст файл `openrouter_models.json` с полным списком доступных моделей.

## Популярные модели OpenRouter (обновлено)

### Бесплатные модели (требуют кредиты, но дешевые):
- `meta-llama/llama-3.1-8b-instruct:free`
- `mistralai/mistral-7b-instruct:free`
- `google/gemini-pro:free` (если доступна)

### Платные модели:
- `openai/gpt-3.5-turbo`
- `openai/gpt-4-turbo`
- `anthropic/claude-3-haiku-20240307`
- `anthropic/claude-3-sonnet-20240229`
- `google/gemini-pro`

## Способ 3: Пересоздать базу данных

Если хотите начать с чистого листа:

```bash
rm chatlist.db
python run.py
```

Приложение автоматически создаст базу данных с актуальными моделями.

## Проверка доступности модели

Перед добавлением модели проверьте её доступность на https://openrouter.ai/models

