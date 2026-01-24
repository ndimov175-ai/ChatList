# Схема базы данных ChatList

## Обзор
База данных SQLite для хранения промптов, моделей нейросетей, результатов и настроек программы.

## Таблицы

### 1. prompts (промпты)
Хранит введенные пользователем запросы и промпты.

| Поле | Тип | Описание | Ограничения |
|------|-----|----------|-------------|
| id | INTEGER | Первичный ключ | PRIMARY KEY AUTOINCREMENT |
| date_created | DATETIME | Дата создания промпта | NOT NULL DEFAULT CURRENT_TIMESTAMP |
| prompt_text | TEXT | Текст промпта | NOT NULL |
| tags | TEXT | Теги для категоризации (JSON массив) | DEFAULT '[]' |
| is_favorite | BOOLEAN | Избранный промпт | DEFAULT 0 |

### 2. models (модели нейросетей)
Хранит информацию о доступных нейросетевых моделях.

| Поле | Тип | Описание | Ограничения |
|------|-----|----------|-------------|
| id | INTEGER | Первичный ключ | PRIMARY KEY AUTOINCREMENT |
| name | VARCHAR(255) | Название модели | NOT NULL UNIQUE |
| api_url | VARCHAR(500) | URL API эндпоинта | NOT NULL |
| api_key_var | VARCHAR(100) | Имя переменной окружения для API ключа | NOT NULL |
| is_active | BOOLEAN | Активна ли модель для запросов | DEFAULT 1 |
| created_at | DATETIME | Дата добавления модели | NOT NULL DEFAULT CURRENT_TIMESTAMP |
| updated_at | DATETIME | Дата последнего обновления | DEFAULT CURRENT_TIMESTAMP |

### 3. results (результаты)
Хранит сохраненные результаты запросов к моделям.

| Поле | Тип | Описание | Ограничения |
|------|-----|----------|-------------|
| id | INTEGER | Первичный ключ | PRIMARY KEY AUTOINCREMENT |
| prompt_id | INTEGER | ID промпта | NOT NULL REFERENCES prompts(id) |
| model_id | INTEGER | ID модели | NOT NULL REFERENCES models(id) |
| response_text | TEXT | Текст ответа модели | NOT NULL |
| response_time | FLOAT | Время ответа в секундах | |
| tokens_used | INTEGER | Количество использованных токенов | |
| saved_at | DATETIME | Дата сохранения | NOT NULL DEFAULT CURRENT_TIMESTAMP |

### 4. settings (настройки)
Хранит настройки программы.

| Поле | Тип | Описание | Ограничения |
|------|-----|----------|-------------|
| id | INTEGER | Первичный ключ | PRIMARY KEY AUTOINCREMENT |
| setting_key | VARCHAR(100) | Ключ настройки | NOT NULL UNIQUE |
| setting_value | TEXT | Значение настройки | NOT NULL |
| setting_type | VARCHAR(50) | Тип значения (string, int, bool, json) | NOT NULL DEFAULT 'string' |
| updated_at | DATETIME | Дата последнего обновления | DEFAULT CURRENT_TIMESTAMP |

## Связи между таблицами

```
prompts (1) ──── (many) results (many) ──── (1) models
```

- Один промпт может иметь много результатов (ответов от разных моделей)
- Одна модель может иметь много результатов (ответов на разные промпты)

## Индексы для оптимизации

```sql
-- Индекс для быстрого поиска по дате создания промптов
CREATE INDEX idx_prompts_date ON prompts(date_created);

-- Индекс для поиска избранных промптов
CREATE INDEX idx_prompts_favorite ON prompts(is_favorite);

-- Индекс для поиска результатов по промпту
CREATE INDEX idx_results_prompt ON results(prompt_id);

-- Индекс для поиска результатов по модели
CREATE INDEX idx_results_model ON results(model_id);

-- Составной индекс для результатов по промпту и модели
CREATE INDEX idx_results_prompt_model ON results(prompt_id, model_id);

-- Индекс для поиска по ключу настройки
CREATE INDEX idx_settings_key ON settings(setting_key);
```

## Примеры настроек

| setting_key | setting_value | setting_type | Описание |
|-------------|---------------|--------------|----------|
| max_concurrent_requests | 3 | int | Максимальное количество одновременных запросов |
| request_timeout | 30 | int | Таймаут запроса в секундах |
| auto_save_results | true | bool | Автоматически сохранять результаты |
| ui_theme | dark | string | Тема интерфейса |
| default_models | ["gpt-4", "claude-3"] | json | Модели по умолчанию |

## Миграции

Для управления изменениями схемы базы данных использовать последовательные SQL файлы миграций в папке `migrations/`.

Пример структуры миграций:
```
migrations/
├── 001_initial_schema.sql
├── 002_add_settings_table.sql
├── 003_add_tokens_field.sql
└── 004_add_favorites.sql
```