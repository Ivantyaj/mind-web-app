# Mindfulness Bot

Бот для mindfulness медитаций, созданный как компаньон для КПТ психолога.

## Функциональность

- Бесплатные медитации (аудио, видео, YouTube)
- 21-дневный курс для премиум пользователей
- Система достижений
- Отслеживание состояния пользователя
- Монетизация через Telegram Stars

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/yourusername/mindfulness-bot.git
cd mindfulness-bot
```

2. Создайте виртуальное окружение и активируйте его:
```bash
python -m venv venv
source venv/bin/activate  # для Linux/Mac
venv\Scripts\activate     # для Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Создайте файл .env и добавьте токен бота:
```
BOT_TOKEN=your_bot_token_here
```

## Запуск

```bash
python bot.py
```

## Структура проекта

- `bot.py` - основной файл бота
- `models.py` - модели базы данных
- `database.py` - работа с базой данных
- `requirements.txt` - зависимости проекта
- `.env` - конфиденциальные данные

## База данных

Проект использует SQLite для хранения данных. База данных создается автоматически при первом запуске. 