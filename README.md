# 📅 NoteSbot — Telegram-ежедневник и заметки

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![pyTelegramBotAPI](https://img.shields.io/badge/pyTelegramBotAPI-4.14+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

![Главное меню бота](<assets/Screenshot 2026-11-19 190830.png>)

Простой и удобный Telegram-бот на Python, который помогает не забывать о делах и сохранять важные заметки. Бот работает локально, хранит данные в SQLite и не требует сторонних сервисов.

## ✨ Возможности

- 📝 **Напоминания** — добавляй дела и указывай точное время или относительное, например `+30m`, `+2h`, `+1d`.
- 🔔 **Автоматические уведомления** — бот пришлёт сообщение, как только наступит нужное время.
- ✅ **Управление делами** — отмечай выполненными или удаляй одним нажатием на Inline-кнопку.
- 📊 **Статистика** — команда `/stats` показывает активные и выполненные дела, дела на сегодня и на неделю, количество заметок и ближайшее напоминание.
- 📒 **Заметки** — сохраняй любые тексты через команду `/note` или кнопку «📒 Добавить заметку».
- 📓 **Список заметок** — просмотр всех заметок кнопкой «📓 Мои заметки» или командой `/notes`.
- 🗑 **Удаление заметок** — по кнопке, без ввода лишних команд.
- 💾 **Две отдельные базы** — напоминания в `reminders.db`, заметки в `notes.db`.
- 🧵 **Фоновый поток** — напоминания проверяются каждые 30 секунд, не блокируя бота.

## 📸 Скриншоты

| Главное меню с кнопками | Статистика |
|---|---|
| ![Кнопки бота](<assets/Screenshot 2026-11-19 190830.png>) | ![Статистика](<assets/Screenshot 2026-11-19 190910.png>) |

## 🛠 Технологии и зависимости

### Обязательные зависимости

| Пакет | Версия | Зачем нужен |
|---|---|---|
| **Python** | **3.10+** | В коде используется синтаксис `datetime \| None` (PEP 604), появившийся в 3.10 |
| **pyTelegramBotAPI** | **4.14.0+** | Основная библиотека для работы с Telegram Bot API |
| **sqlite3** | встроен в Python | База данных (устанавливать не нужно) |
| **datetime** | встроен в Python | Работа с датами и временем |
| **threading** | встроен в Python | Фоновый поток для проверки напоминаний |
| **re** | встроен в Python | Регулярные выражения для парсинга `+30m` |
| **time** | встроен в Python | Пауза `time.sleep(30)` в фоновом потоке |

### Установка обязательных зависимостей

```bash
pip install pyTelegramBotAPI
```

Или с фиксацией версии:

```bash
pip install pyTelegramBotAPI==4.14.0
```

### Проверка версий

```bash
python --version
# Должно быть Python 3.10 или выше

pip show pyTelegramBotAPI
# Должна быть версия 4.14.0 или выше
```

### Опциональные зависимости (для разработки)

| Пакет | Версия | Зачем нужен |
|---|---|---|
| **python-dotenv** | 1.0.0+ | Хранить токен в `.env` вместо `config.py` |
| **black** | 23.0+ | Автоформатирование кода |
| **flake8** | 6.0+ | Проверка стиля кода |
| **pytest** | 7.0+ | Юнит-тесты для `parse_when`, `get_stats` и т.д. |
| **mypy** | 1.0+ | Статическая проверка типов |

Установка опциональных:

```bash
pip install python-dotenv black flake8 pytest mypy
```

### Использование `.env` вместо `config.py` (опционально)

**1. Установи `python-dotenv`:**
```bash
pip install python-dotenv
```

**2. Создай `.env` в корне проекта:**
```
BOT_TOKEN=1234567890:AAHxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**3. Добавь `.env` в `.gitignore`:**
```
.env
*.db
__pycache__/
```

**4. Замени в `bot.py` импорт:**
```python
import os
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("BOT_TOKEN")
```

## 📦 Установка и запуск

### 1. Установи зависимости
```bash
pip install pyTelegramBotAPI
```

### 2. Создай файл `config.py`
```python
token = "ТВОЙ_ТОКЕН_ОТ_BOTFATHER"
```

### 3. Запусти бота
```bash
python bot.py
```

При первом запуске автоматически создадутся два файла базы данных: `reminders.db` и `notes.db`.

## 📁 Структура проекта

```
NoteSbot/
├── assets/
│   ├── Screenshot 2026-11-19 190830.png
│   └── Screenshot 2026-11-19 190910.png
├── bot.py              # основная логика бота
├── database.py         # работа с SQLite
├── config.py           # токен бота
├── reminders.db        # база напоминаний (создаётся автоматически)
├── notes.db            # база заметок (создаётся автоматически)
└── README.md
```

## 🎮 Команды и кнопки

| Команда | Кнопка | Что делает |
|---|---|---|
| `/start` | — | Приветствие и клавиатура |
| `/help` | — | Справка по использованию |
| `/add` | 📝 Добавить дело | Пошаговое добавление дела |
| `/list` | 📋 Мои дела | Список активных дел |
| `/note <текст>` | 📒 Добавить заметку | Сохранить заметку |
| `/notes` | 📓 Мои заметки | Показать все заметки |
| `/stats` | 📊 Статистика | Статистика по делам и заметкам |
| `/cancel` | — | Отменить текущий ввод |
| `/delnote <id>` | — | Удалить заметку по ID |

## 🕐 Форматы времени для напоминаний

- **Абсолютное:** `ДД.ММ.ГГГГ ЧЧ:ММ` — например, `25.12.2026 09:00`
- **Относительное:** `+N m/h/d` — например:
  - `+30m` — через 30 минут
  - `+2h` — через 2 часа
  - `+1d` — через 1 день

## 💡 Пример использования

1. Нажми **📝 Добавить дело**.
2. Напиши: `Позвонить маме`.
3. Укажи время: `+2h`.
4. Бот подтвердит: «✅ Записал! …»
5. Через 2 часа придёт: «🔔 Напоминание! Позвонить маме».
6. Отметь дело кнопкой **✅ Выполнено** — оно попадёт в статистику.

## 🗄 База данных

**`reminders.db`**
```sql
CREATE TABLE reminders (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    text TEXT NOT NULL,
    remind_at TEXT NOT NULL,
    done INTEGER DEFAULT 0
);
```

**`notes.db`**
```sql
CREATE TABLE notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    text TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now'))
);
```

## ⚠️ Важно

- Для работы нужен **Python 3.10+**.
- «✅ Выполнено» **не удаляет** дело, а ставит `done = 1`. Оно пропадает из списка и напоминаний, но остаётся в статистике.
- «🗑 Удалить» удаляет запись физически.
- Бот технически поддерживает несколько `user_id` — данные разделены по пользователю.
- Файлы `reminders.db` и `notes.db` **не коммить** в git — добавь их в `.gitignore`.

## 🧪 Тестирование (опционально)

Если установил `pytest`:

```bash
pytest tests/ -v
```

Пример теста для `parse_when`:

```python
from datetime import datetime
from bot import parse_when

def test_relative_minutes():
    now = datetime.now()
    result = parse_when("+30m")
    assert result is not None
    diff = (result - now).total_seconds()
    assert 1795 < diff < 1805
```

## 🐳 Docker (опционально)

**`Dockerfile`:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "bot.py"]
```

**`requirements.txt`:**
```
pyTelegramBotAPI>=4.14.0
```

**`docker-compose.yml`:**
```yaml
version: "3.9"
services:
  notesbot:
    build: .
    restart: unless-stopped
    volumes:
      - ./data:/app
    environment:
      - BOT_TOKEN=${BOT_TOKEN}
```

Запуск:
```bash
docker-compose up -d
```

## 📄 Лицензия

MIT — используй свободно.
