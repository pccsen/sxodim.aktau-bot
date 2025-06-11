# Sxodim.Aktau Telegram Bot — demo-v1.0

## Стек и фреймворки
- Python 3.12+
- [aiogram 3.x](https://docs.aiogram.dev/en/latest/) — Telegram Bot API
- [FastAPI](https://fastapi.tiangolo.com/) — REST API
- [SQLAlchemy](https://www.sqlalchemy.org/) — ORM для работы с БД
- [Alembic](https://alembic.sqlalchemy.org/) — миграции БД
- [Pydantic](https://docs.pydantic.dev/) — валидация данных
- [Uvicorn](https://www.uvicorn.org/) — ASGI сервер
- [python-dotenv](https://pypi.org/project/python-dotenv/) — переменные окружения
- SQLite (по умолчанию, можно заменить на PostgreSQL/MySQL)

Бот-афиша для города Актау 🇰🇿: ближайшие мероприятия, акции, избранное, поиск, обратная связь, админ-панель и рассылки.

## Возможности
- Мультиязычность (RU/KZ/EN)
- Поиск мероприятий по дате и категории
- Избранное для пользователей
- Подписка на уведомления
- FAQ и поддержка
- Админ-панель: добавление, редактирование, удаление мероприятий и акций
- Массовая рассылка
- Статистика
- Инлайн-кнопки для действий с мероприятиями
- Меню команд как у BotFather

## Быстрый старт

### 1. Клонируйте репозиторий и перейдите в папку проекта
```bash
cd sxodim-aktau
```

### 2. Установите зависимости
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Настройте переменные окружения
Создайте файл `.env` в корне проекта:
```
BOT_TOKEN=ваш_токен_бота_от_BotFather
ADMIN_IDS=123456789
DATABASE_URL=sqlite:///bot.db
```

### 4. Запустите бота и сервер
```bash
python main.py
```

### 5. Добавьте меню команд через @BotFather
Выполните `/setcommands` и вставьте:
```
start - Главное меню
help - Помощь и справка
upcoming_event - Ближайшие мероприятия
promotions_in_public_catering - Акции в заведениях
feedback - Оставить отзыв
search - Поиск мероприятий
favorites - Избранное
subscribe - Подписка на уведомления
language - Сменить язык
admin - Админ-панель
stats - Статистика
broadcast - Рассылка
faq - Часто задаваемые вопросы
contact - Связь с поддержкой
```

## Для админа
- Используйте команду `/admin` для доступа к панели управления.
- Для рассылки: `/broadcast текст_рассылки`
- Для статистики: `/stats`

## Demo-v1.0
- Минимальный стабильный функционал для пользователей и админов.
- Готов к расширению: интеграции, новые роли, веб-админка, мобильное приложение.

---

**Если возникнут вопросы — пишите telegram:@senwjuzz!** 