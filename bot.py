import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
    ConversationHandler,
)

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [int(id) for id in os.getenv("ADMIN_IDS", "").split(",") if id]

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
(
    ADDING_EVENT,
    EDITING_EVENT,
    FEEDBACK,
    PROMOTION,
) = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    welcome_text = (
        f"👋 Привет, {user.first_name}!\n\n"
        "Я бот-афиша, который поможет вам узнать о ближайших мероприятиях "
        "и акциях в заведениях общепита.\n\n"
        "Доступные команды:\n"
        "/help - Справка по использованию\n"
        "/upcoming_event - Ближайшие мероприятия\n"
        "/feedback - Оставить отзыв\n"
        "/promotions_in_public_catering - Акции в заведениях"
    )
    await update.message.reply_text(welcome_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    help_text = (
        "📚 Справка по использованию бота:\n\n"
        "1. /upcoming_event - Показывает ближайшие мероприятия\n"
        "2. /feedback - Позволяет оставить отзыв\n"
        "3. /promotions_in_public_catering - Показывает акции в заведениях\n\n"
        "Для менеджеров доступна дополнительная панель управления."
    )
    await update.message.reply_text(help_text)

async def upcoming_event(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show upcoming events."""
    # TODO: Implement event fetching from database
    await update.message.reply_text("Здесь будет список ближайших мероприятий")

async def feedback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the feedback process."""
    await update.message.reply_text(
        "Пожалуйста, напишите ваш отзыв или предложение:"
    )
    return FEEDBACK

async def handle_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle the feedback message."""
    feedback_text = update.message.text
    # TODO: Save feedback to database
    await update.message.reply_text("Спасибо за ваш отзыв!")
    return ConversationHandler.END

async def promotions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show promotions in public catering."""
    # TODO: Implement promotions fetching from database
    await update.message.reply_text("Здесь будут акции в заведениях")

def is_admin(user_id: int) -> bool:
    """Check if user is an admin."""
    return user_id in ADMIN_IDS

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show admin panel if user is admin."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("У вас нет доступа к панели администратора.")
        return

    keyboard = [
        [
            InlineKeyboardButton("➕ Добавить мероприятие", callback_data="add_event"),
            InlineKeyboardButton("✏️ Редактировать", callback_data="edit_event"),
        ],
        [
            InlineKeyboardButton("🗑 Удалить", callback_data="delete_event"),
            InlineKeyboardButton("📋 Список мероприятий", callback_data="list_events"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Панель управления мероприятиями:", reply_markup=reply_markup
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button callbacks."""
    query = update.callback_query
    await query.answer()

    if query.data == "add_event":
        await query.message.reply_text("Введите название мероприятия:")
        return ADDING_EVENT
    elif query.data == "edit_event":
        # TODO: Implement event editing
        await query.message.reply_text("Выберите мероприятие для редактирования:")
    elif query.data == "delete_event":
        # TODO: Implement event deletion
        await query.message.reply_text("Выберите мероприятие для удаления:")
    elif query.data == "list_events":
        # TODO: Implement event listing
        await query.message.reply_text("Список мероприятий:")

def main() -> None:
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add conversation handler for feedback
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("feedback", feedback)],
        states={
            FEEDBACK: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_feedback)],
        },
        fallbacks=[],
    )

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("upcoming_event", upcoming_event))
    application.add_handler(CommandHandler("promotions_in_public_catering", promotions))
    application.add_handler(CommandHandler("admin", admin_panel))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(conv_handler)

    # Start the Bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main() 