from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandObject
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from datetime import datetime
import asyncio
from sqlalchemy import Column, Integer, String

from app.core.config import settings
from app.database.database import get_db
from app.models.event import Event
from app.models.promotion import Promotion
from app.models.feedback import Feedback
from app.models.favorite import Favorite
from app.models.subscriber import Subscriber
from app.models.base import BaseModel

CATEGORIES = [
    "Вечеринка",
    "Концерт",
    "Встреча",
    "Акция",
    "Другое"
]

# Модель для хранения языка пользователя
class UserLang(BaseModel):
    __tablename__ = "user_langs"
    user_id = Column(Integer, unique=True, nullable=False)
    lang = Column(String(5), default="ru")

# Словари переводов
TRANSLATIONS = {
    "ru": {
        "welcome": "Привет! 👋\nТы в боте Sxodim.Aktau — афише самых интересных мероприятий в городе Актау 🇰🇿\n\n📆 Тут ты найдёшь:\n— ближайшие вечеринки, концерты и встречи\n— акции в кафе, ресторанах и местах отдыха\n— полезную информацию и обратную связь\n\nКоманды, которые тебе доступны:\n/upcoming_event — ближайшие мероприятия\n/promotions_in_public_catering — акции в заведениях\n/feedback — оставить отзыв\n/help — помощь и справка\n\nОставайся с нами и не пропусти ничего интересного! 🎊",
        "choose_lang": "Выберите язык / Тілді таңдаңыз / Select language:",
        "lang_set": "Язык успешно изменён!"
    },
    "kz": {
        "welcome": "Сәлем! 👋\nСен Sxodim.Aktau ботындасың — Ақтаудағы ең қызықты іс-шаралардың афишасы 🇰🇿\n\n📆 Мұнда сен табасың:\n— жақын кештер, концерттер және кездесулер\n— дәмханалар мен мейрамханалардағы акциялар\n— пайдалы ақпарат және кері байланыс\n\nҚол жетімді командалар:\n/upcoming_event — жақын іс-шаралар\n/promotions_in_public_catering — акциялар\n/feedback — пікір қалдыру\n/help — көмек және анықтама\n\nБізбен бірге бол және ештеңені жіберіп алма! 🎊",
        "choose_lang": "Выберите язык / Тілді таңдаңыз / Select language:",
        "lang_set": "Тіл сәтті өзгертілді!"
    },
    "en": {
        "welcome": "Hi! 👋\nYou are in Sxodim.Aktau bot — the poster of the most interesting events in Aktau 🇰🇿\n\n📆 Here you will find:\n— upcoming parties, concerts and meetings\n— promotions in cafes, restaurants and leisure places\n— useful information and feedback\n\nAvailable commands:\n/upcoming_event — upcoming events\n/promotions_in_public_catering — promotions\n/feedback — leave feedback\n/help — help and info\n\nStay with us and don't miss anything interesting! 🎊",
        "choose_lang": "Выберите язык / Тілді таңдаңыз / Select language:",
        "lang_set": "Language changed successfully!"
    }
}

LANGS = [
    ("Русский", "ru"),
    ("Қазақша", "kz"),
    ("English", "en")
]

# Initialize bot and dispatcher
bot = Bot(token=settings.BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# States
class EventStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_date = State()
    waiting_for_location = State()

class PromotionStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_venue = State()
    waiting_for_dates = State()

class FeedbackStates(StatesGroup):
    waiting_for_message = State()

class EditEventStates(StatesGroup):
    waiting_for_field = State()
    waiting_for_value = State()
    event_id = State()
    field = State()

class EditPromoStates(StatesGroup):
    waiting_for_field = State()
    waiting_for_value = State()
    promo_id = State()
    field = State()

USER_MENU = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Ближайшие мероприятия"), KeyboardButton(text="Акции")],
        [KeyboardButton(text="Поиск"), KeyboardButton(text="Избранное")],
        [KeyboardButton(text="Оставить отзыв"), KeyboardButton(text="Помощь")],
        [KeyboardButton(text="Язык")]
    ],
    resize_keyboard=True
)

ADMIN_MENU = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Ближайшие мероприятия"), KeyboardButton(text="Акции")],
        [KeyboardButton(text="Поиск"), KeyboardButton(text="Избранное")],
        [KeyboardButton(text="Оставить отзыв"), KeyboardButton(text="Помощь")],
        [KeyboardButton(text="Язык")],
        [KeyboardButton(text="Админ-панель"), KeyboardButton(text="Статистика")],
        [KeyboardButton(text="Рассылка")]
    ],
    resize_keyboard=True
)

# Command handlers
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    lang = get_user_lang(message.from_user.id)
    await message.answer(TRANSLATIONS[lang]["welcome"], reply_markup=ReplyKeyboardRemove())

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    help_text = (
        "📚 Справка по использованию бота:\n\n"
        "1. /upcoming_event - Показывает ближайшие мероприятия\n"
        "2. /feedback - Позволяет оставить отзыв\n"
        "3. /promotions_in_public_catering - Показывает акции в заведениях\n\n"
        "Для менеджеров доступна дополнительная панель управления."
    )
    await message.answer(help_text)

@dp.message(Command("upcoming_event"))
async def cmd_upcoming_events(message: types.Message):
    db = next(get_db())
    events = db.query(Event).filter(Event.date >= datetime.utcnow()).order_by(Event.date).limit(5).all()
    
    if not events:
        await message.answer("На данный момент нет предстоящих мероприятий.")
        return

    for event in events:
        event_text = (
            f"🎉 {event.title}\n\n"
            f"📅 Дата: {event.date.strftime('%d.%m.%Y %H:%M')}\n"
            f"📍 Место: {event.location}\n\n"
            f"{event.description}"
        )
        inline_kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="⭐️ В избранное", callback_data=f"fav_{event.id}")],
                [InlineKeyboardButton(text="Подробнее", callback_data=f"details_{event.id}")],
                [InlineKeyboardButton(text="Поделиться", switch_inline_query=event.title)]
            ]
        )
        await message.answer(event_text, reply_markup=inline_kb)

@dp.message(Command("feedback"))
async def cmd_feedback(message: types.Message, state: FSMContext):
    await message.answer("Пожалуйста, напишите ваш отзыв или предложение:")
    await state.set_state(FeedbackStates.waiting_for_message)

@dp.message(FeedbackStates.waiting_for_message)
async def process_feedback(message: types.Message, state: FSMContext):
    db = next(get_db())
    feedback = Feedback(user_id=message.from_user.id, message=message.text)
    db.add(feedback)
    db.commit()
    await message.answer("Спасибо за ваш отзыв! 🙏")
    await state.clear()

@dp.message(Command("promotions_in_public_catering"))
async def cmd_promotions(message: types.Message):
    db = next(get_db())
    promotions = db.query(Promotion).filter(Promotion.is_active == True).all()
    
    if not promotions:
        await message.answer("На данный момент нет активных акций.")
        return

    for promotion in promotions:
        promotion_text = (
            f"🏷 {promotion.title}\n\n"
            f"📝 {promotion.description}\n"
            f"🏪 Место: {promotion.location}\n"
            f"📅 Действует до: {promotion.end_date.strftime('%d.%m.%Y')}"
        )
        await message.answer(promotion_text)

@dp.message(Command("admin"))
async def cmd_admin(message: types.Message):
    if message.from_user.id not in settings.get_admin_ids():
        await message.answer("У вас нет доступа к админ-панели.")
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="➕ Добавить мероприятие", callback_data="add_event"),
            InlineKeyboardButton(text="➕ Добавить акцию", callback_data="add_promotion")
        ],
        [
            InlineKeyboardButton(text="📋 Список мероприятий", callback_data="list_events"),
            InlineKeyboardButton(text="📋 Список акций", callback_data="list_promotions")
        ]
    ])
    
    await message.answer("Панель управления:", reply_markup=keyboard)

@dp.message(Command("search"))
async def cmd_search(message: types.Message, state: FSMContext):
    # Клавиатура для выбора поиска
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Поиск по дате")],
            [KeyboardButton(text="Поиск по категории")]
        ],
        resize_keyboard=True
    )
    await message.answer("Как вы хотите искать мероприятие?", reply_markup=keyboard)
    await state.set_state("search:choose_mode")

@dp.message(lambda m: m.text == "Поиск по дате")
async def search_by_date(message: types.Message, state: FSMContext):
    await message.answer("Введите дату в формате ДД.ММ.ГГГГ:", reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Меню")]], resize_keyboard=True))
    await state.set_state("search:wait_date")

@dp.message(lambda m: m.text == "Поиск по категории")
async def search_by_category(message: types.Message, state: FSMContext):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=cat)] for cat in CATEGORIES] + [[KeyboardButton(text="Меню")]],
        resize_keyboard=True
    )
    await message.answer("Выберите категорию:", reply_markup=keyboard)
    await state.set_state("search:wait_category")

@dp.message(lambda m: m.text == "Меню")
async def back_to_menu(message: types.Message):
    lang = get_user_lang(message.from_user.id)
    await message.answer("Главное меню:", reply_markup=ReplyKeyboardRemove())

@dp.message(lambda m: m.text in CATEGORIES)
async def process_search_category(message: types.Message, state: FSMContext):
    category = message.text
    db = next(get_db())
    events = db.query(Event).filter(Event.description.ilike(f"%{category}%")).all()
    if not events:
        await message.answer("Мероприятий по выбранной категории не найдено.")
    else:
        for event in events:
            event_text = (
                f"🎉 {event.title}\n\n"
                f"📅 Дата: {event.date.strftime('%d.%m.%Y %H:%M')}\n"
                f"📍 Место: {event.location}\n\n"
                f"{event.description}"
            )
            inline_kb = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="⭐️ В избранное", callback_data=f"fav_{event.id}")],
                    [InlineKeyboardButton(text="Подробнее", callback_data=f"details_{event.id}")],
                    [InlineKeyboardButton(text="Поделиться", switch_inline_query=event.title)]
                ]
            )
            await message.answer(event_text, reply_markup=inline_kb)
    await state.clear()

@dp.message()
async def process_search_date(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == "search:wait_date":
        try:
            date = datetime.strptime(message.text, "%d.%m.%Y")
        except ValueError:
            await message.answer("Неверный формат даты. Введите в формате ДД.ММ.ГГГГ:")
            return
        db = next(get_db())
        events = db.query(Event).filter(Event.date >= date, Event.date < date.replace(hour=23, minute=59, second=59)).all()
        if not events:
            await message.answer("Мероприятий на эту дату не найдено.")
        else:
            for event in events:
                event_text = (
                    f"🎉 {event.title}\n\n"
                    f"📅 Дата: {event.date.strftime('%d.%m.%Y %H:%M')}\n"
                    f"📍 Место: {event.location}\n\n"
                    f"{event.description}"
                )
                inline_kb = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [InlineKeyboardButton(text="⭐️ В избранное", callback_data=f"fav_{event.id}")],
                        [InlineKeyboardButton(text="Подробнее", callback_data=f"details_{event.id}")],
                        [InlineKeyboardButton(text="Поделиться", switch_inline_query=event.title)]
                    ]
                )
                await message.answer(event_text, reply_markup=inline_kb)
        await state.clear()

@dp.message(Command("subscribe"))
async def cmd_subscribe(message: types.Message):
    db = next(get_db())
    user_id = message.from_user.id
    exists = db.query(Subscriber).filter_by(user_id=user_id).first()
    if not exists:
        db.add(Subscriber(user_id=user_id))
        db.commit()
        await message.answer("Вы подписались на уведомления о новых мероприятиях!")
    else:
        await message.answer("Вы уже подписаны на уведомления.")

@dp.message(Command("favorites"))
async def cmd_favorites(message: types.Message):
    db = next(get_db())
    favs = db.query(Favorite).filter_by(user_id=message.from_user.id).all()
    if not favs:
        await message.answer("У вас пока нет избранных мероприятий.")
        return
    for fav in favs:
        event = db.query(Event).filter_by(id=fav.event_id).first()
        if event:
            event_text = (
                f"🎉 {event.title}\n\n"
                f"📅 Дата: {event.date.strftime('%d.%m.%Y %H:%M')}\n"
                f"📍 Место: {event.location}\n\n"
                f"{event.description}"
            )
            await message.answer(event_text)

@dp.message(Command("broadcast"))
async def cmd_broadcast(message: types.Message, command: CommandObject):
    if message.from_user.id not in settings.get_admin_ids():
        await message.answer("У вас нет доступа к этой команде.")
        return
    text = command.args or None
    if not text:
        await message.answer("Введите текст рассылки после команды, например: /broadcast Сегодня новое мероприятие!")
        return
    db = next(get_db())
    subscribers = db.query(Subscriber).all()
    count = 0
    for sub in subscribers:
        try:
            await bot.send_message(sub.user_id, f"📢 {text}")
            count += 1
        except Exception:
            pass
    await message.answer(f"Рассылка отправлена {count} подписчикам.")

@dp.message(Command("faq"))
async def cmd_faq(message: types.Message):
    faq_text = (
        "❓ <b>Часто задаваемые вопросы</b>\n\n"
        "<b>Как добавить мероприятие?</b>\n"
        "— Только администратор может добавлять мероприятия через /admin.\n\n"
        "<b>Как попасть в избранное?</b>\n"
        "— Нажмите ⭐️ под интересующим мероприятием.\n\n"
        "<b>Как подписаться на рассылку?</b>\n"
        "— Используйте команду /subscribe.\n\n"
        "<b>Как связаться с поддержкой?</b>\n"
        "— Используйте команду /contact."
    )
    await message.answer(faq_text, parse_mode="HTML")

@dp.message(Command("contact"))
async def cmd_contact(message: types.Message):
    await message.answer("📞 Для связи с поддержкой напишите: @your_support_username или на email: support@example.com")

@dp.message(Command("language"))
async def cmd_language(message: types.Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=title, callback_data=f"lang_{code}")] for title, code in LANGS
        ]
    )
    await message.answer(TRANSLATIONS["ru"]["choose_lang"], reply_markup=keyboard)

@dp.callback_query(lambda c: c.data.startswith("lang_"))
async def set_language(callback_query: types.CallbackQuery):
    lang = callback_query.data.split("_", 1)[1]
    db = next(get_db())
    user_id = callback_query.from_user.id
    user_lang = db.query(UserLang).filter_by(user_id=user_id).first()
    if not user_lang:
        db.add(UserLang(user_id=user_id, lang=lang))
    else:
        user_lang.lang = lang
    db.commit()
    await callback_query.answer(TRANSLATIONS[lang]["lang_set"])

@dp.message(Command("stats"))
async def cmd_stats(message: types.Message):
    if message.from_user.id not in settings.get_admin_ids():
        await message.answer("У вас нет доступа к этой команде.")
        return
    db = next(get_db())
    users = db.query(UserLang).count()
    subscribers = db.query(Subscriber).count()
    events = db.query(Event).count()
    promotions = db.query(Promotion).count()
    favorites = db.query(Favorite).count()
    text = (
        f"📊 <b>Статистика</b>\n\n"
        f"👤 Пользователей: <b>{users}</b>\n"
        f"🔔 Подписчиков: <b>{subscribers}</b>\n"
        f"🎉 Мероприятий: <b>{events}</b>\n"
        f"🎁 Акций: <b>{promotions}</b>\n"
        f"⭐️ Избранных: <b>{favorites}</b>"
    )
    await message.answer(text, parse_mode="HTML")

# Event handlers
@dp.callback_query(lambda c: c.data == "add_event")
async def process_add_event(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.from_user.id not in settings.get_admin_ids():
        await callback_query.answer("У вас нет доступа к этой функции.")
        return
    
    await callback_query.message.answer("Введите название мероприятия:")
    await state.set_state(EventStates.waiting_for_title)

@dp.message(EventStates.waiting_for_title)
async def process_event_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Введите описание мероприятия:")
    await state.set_state(EventStates.waiting_for_description)

@dp.message(EventStates.waiting_for_description)
async def process_event_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Введите дату и время мероприятия (в формате ДД.ММ.ГГГГ ЧЧ:ММ):")
    await state.set_state(EventStates.waiting_for_date)

@dp.message(EventStates.waiting_for_date)
async def process_event_date(message: types.Message, state: FSMContext):
    try:
        date = datetime.strptime(message.text, "%d.%m.%Y %H:%M")
        await state.update_data(date=date)
        await message.answer("Введите место проведения мероприятия:")
        await state.set_state(EventStates.waiting_for_location)
    except ValueError:
        await message.answer("Неверный формат даты. Пожалуйста, используйте формат ДД.ММ.ГГГГ ЧЧ:ММ")

@dp.message(EventStates.waiting_for_location)
async def process_event_location(message: types.Message, state: FSMContext):
    data = await state.get_data()
    db = next(get_db())
    
    event = Event(
        title=data['title'],
        description=data['description'],
        date=data['date'],
        location=message.text
    )
    
    db.add(event)
    db.commit()
    
    await message.answer("✅ Мероприятие успешно добавлено!")
    await state.clear()

# Promotion handlers
@dp.callback_query(lambda c: c.data == "add_promotion")
async def process_add_promotion(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.from_user.id not in settings.get_admin_ids():
        await callback_query.answer("У вас нет доступа к этой функции.")
        return
    
    await callback_query.message.answer("Введите название акции:")
    await state.set_state(PromotionStates.waiting_for_title)

@dp.message(PromotionStates.waiting_for_title)
async def process_promotion_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Введите описание акции:")
    await state.set_state(PromotionStates.waiting_for_description)

@dp.message(PromotionStates.waiting_for_description)
async def process_promotion_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Введите название заведения:")
    await state.set_state(PromotionStates.waiting_for_venue)

@dp.message(PromotionStates.waiting_for_venue)
async def process_promotion_venue(message: types.Message, state: FSMContext):
    await state.update_data(venue=message.text)
    await message.answer("Введите период действия акции (например, 'до 31.12.2024'):")
    await state.set_state(PromotionStates.waiting_for_dates)

@dp.message(PromotionStates.waiting_for_dates)
async def process_promotion_dates(message: types.Message, state: FSMContext):
    data = await state.get_data()
    db = next(get_db())
    
    promotion = Promotion(
        title=data['title'],
        description=data['description'],
        venue=data['venue'],
        valid_until=message.text
    )
    
    db.add(promotion)
    db.commit()
    
    await message.answer("✅ Акция успешно добавлена!")
    await state.clear()

# List handlers
@dp.callback_query(lambda c: c.data == "list_events")
async def process_list_events(callback_query: types.CallbackQuery):
    if callback_query.from_user.id not in settings.get_admin_ids():
        await callback_query.answer("У вас нет доступа к этой функции.")
        return
    db = next(get_db())
    events = db.query(Event).order_by(Event.date).all()
    if not events:
        await callback_query.message.answer("Список мероприятий пуст.")
        return
    for event in events:
        event_text = (
            f"🎉 {event.title}\n\n"
            f"📅 Дата: {event.date.strftime('%d.%m.%Y %H:%M')}\n"
            f"📍 Место: {event.location}\n\n"
            f"{event.description}"
        )
        inline_kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="⭐️ В избранное", callback_data=f"fav_{event.id}")],
                [InlineKeyboardButton(text="Подробнее", callback_data=f"details_{event.id}")],
                [InlineKeyboardButton(text="Поделиться", switch_inline_query=event.title)]
            ]
        )
        await callback_query.message.answer(event_text, reply_markup=inline_kb)

@dp.callback_query(lambda c: c.data == "list_promotions")
async def process_list_promotions(callback_query: types.CallbackQuery):
    if callback_query.from_user.id not in settings.get_admin_ids():
        await callback_query.answer("У вас нет доступа к этой функции.")
        return
    db = next(get_db())
    promotions = db.query(Promotion).all()
    if not promotions:
        await callback_query.message.answer("Список акций пуст.")
        return
    for promotion in promotions:
        promotion_text = (
            f"🎁 {promotion.title}\n\n"
            f"🏪 Заведение: {promotion.venue}\n"
            f"⏰ Действует: {promotion.valid_until}\n\n"
            f"{promotion.description}"
        )
        await callback_query.message.answer(promotion_text)

# Обработчик добавления в избранное
@dp.callback_query(lambda c: c.data.startswith("fav_"))
async def add_to_favorites(callback_query: types.CallbackQuery):
    event_id = int(callback_query.data.split("_", 1)[1])
    db = next(get_db())
    user_id = callback_query.from_user.id
    # Проверка на дубли
    exists = db.query(Favorite).filter_by(user_id=user_id, event_id=event_id).first()
    if not exists:
        db.add(Favorite(user_id=user_id, event_id=event_id))
        db.commit()
        await callback_query.answer("Добавлено в избранное!")
    else:
        await callback_query.answer("Уже в избранном.")

# Удаление мероприятия
@dp.callback_query(lambda c: c.data.startswith("delete_event_"))
async def delete_event(callback_query: types.CallbackQuery):
    if callback_query.from_user.id not in settings.get_admin_ids():
        await callback_query.answer("Нет доступа.")
        return
    event_id = int(callback_query.data.split("_", 2)[2])
    db = next(get_db())
    event = db.query(Event).filter_by(id=event_id).first()
    if event:
        db.delete(event)
        db.commit()
        await callback_query.message.answer("Мероприятие удалено.")
    else:
        await callback_query.message.answer("Мероприятие не найдено.")

# Редактирование мероприятия (пошагово)
@dp.callback_query(lambda c: c.data.startswith("edit_event_"))
async def edit_event_start(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.from_user.id not in settings.get_admin_ids():
        await callback_query.answer("Нет доступа.")
        return
    event_id = int(callback_query.data.split("_", 2)[2])
    await state.update_data(event_id=event_id)
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Название", callback_data="edit_field_title")],
            [InlineKeyboardButton(text="Описание", callback_data="edit_field_description")],
            [InlineKeyboardButton(text="Дата", callback_data="edit_field_date")],
            [InlineKeyboardButton(text="Место", callback_data="edit_field_location")]
        ]
    )
    await callback_query.message.answer("Что вы хотите изменить?", reply_markup=keyboard)
    await state.set_state(EditEventStates.waiting_for_field)

@dp.callback_query(lambda c: c.data.startswith("edit_field_"))
async def edit_event_field(callback_query: types.CallbackQuery, state: FSMContext):
    field = callback_query.data.split("_", 2)[2]
    await state.update_data(field=field)
    await callback_query.message.answer(f"Введите новое значение для поля: {field}")
    await state.set_state(EditEventStates.waiting_for_value)

@dp.message(EditEventStates.waiting_for_value)
async def edit_event_value(message: types.Message, state: FSMContext):
    data = await state.get_data()
    event_id = data["event_id"]
    field = data["field"]
    db = next(get_db())
    event = db.query(Event).filter_by(id=event_id).first()
    if not event:
        await message.answer("Мероприятие не найдено.")
        await state.clear()
        return
    value = message.text
    if field == "date":
        try:
            value = datetime.strptime(value, "%d.%m.%Y %H:%M")
        except ValueError:
            await message.answer("Неверный формат даты. Введите в формате ДД.ММ.ГГГГ ЧЧ:ММ")
            return
    setattr(event, field, value)
    db.commit()
    await message.answer(f"Поле {field} успешно обновлено!")
    await state.clear()

# Удаление акции
@dp.callback_query(lambda c: c.data.startswith("delete_promo_"))
async def delete_promotion(callback_query: types.CallbackQuery):
    if callback_query.from_user.id not in settings.get_admin_ids():
        await callback_query.answer("Нет доступа.")
        return
    promo_id = int(callback_query.data.split("_", 2)[2])
    db = next(get_db())
    promo = db.query(Promotion).filter_by(id=promo_id).first()
    if promo:
        db.delete(promo)
        db.commit()
        await callback_query.message.answer("Акция удалена.")
    else:
        await callback_query.message.answer("Акция не найдена.")

# Редактирование акции (пошагово)
@dp.callback_query(lambda c: c.data.startswith("edit_promo_"))
async def edit_promo_start(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.from_user.id not in settings.get_admin_ids():
        await callback_query.answer("Нет доступа.")
        return
    promo_id = int(callback_query.data.split("_", 2)[2])
    await state.update_data(promo_id=promo_id)
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Название", callback_data="edit_promo_field_title")],
            [InlineKeyboardButton(text="Описание", callback_data="edit_promo_field_description")],
            [InlineKeyboardButton(text="Заведение", callback_data="edit_promo_field_venue")],
            [InlineKeyboardButton(text="Срок действия", callback_data="edit_promo_field_valid_until")]
        ]
    )
    await callback_query.message.answer("Что вы хотите изменить?", reply_markup=keyboard)
    await state.set_state(EditPromoStates.waiting_for_field)

@dp.callback_query(lambda c: c.data.startswith("edit_promo_field_"))
async def edit_promo_field(callback_query: types.CallbackQuery, state: FSMContext):
    field = callback_query.data.split("_", 3)[3]
    await state.update_data(field=field)
    await callback_query.message.answer(f"Введите новое значение для поля: {field}")
    await state.set_state(EditPromoStates.waiting_for_value)

@dp.message(EditPromoStates.waiting_for_value)
async def edit_promo_value(message: types.Message, state: FSMContext):
    data = await state.get_data()
    promo_id = data["promo_id"]
    field = data["field"]
    db = next(get_db())
    promo = db.query(Promotion).filter_by(id=promo_id).first()
    if not promo:
        await message.answer("Акция не найдена.")
        await state.clear()
        return
    value = message.text
    setattr(promo, field, value)
    db.commit()
    await message.answer(f"Поле {field} успешно обновлено!")
    await state.clear()

# Функция для получения языка пользователя
def get_user_lang(user_id):
    db = next(get_db())
    user_lang = db.query(UserLang).filter_by(user_id=user_id).first()
    return user_lang.lang if user_lang else "ru"

async def start_bot():
    print("Bot polling started!")
    await dp.start_polling(bot) 