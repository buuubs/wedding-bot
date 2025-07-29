python-telegram-bot==20.8
import os
import logging
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler

# Настройки логов
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Переменные окружения
TOKEN = os.getenv("TELEGRAM_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

# Данные
checklist = [
    "📆 Назначить дату свадьбы",
    "👗 Купить платье и костюм",
    "📜 Подать заявление в ЗАГС",
    "🏛️ Забронировать ресторан",
    "📷 Найти фотографа/видеографа",
    "🎵 Выбрать музыку",
    "💌 Отправить приглашения",
    "💍 Купить кольца"
]

guests = {}  # {имя: статус}
budget = []  # [{type: 'расход'/'доход', amount: int, note: str}]
reminders = []  # список строк
zagc_address = "ул. Свадебная, 1"
restaurant_address = "пр. Любви, 5"

# --- Команды ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👰🤵 Привет! Я свадебный помощник.\n\n"
        "Команды:\n"
        "/checklist – чек-лист подготовки\n"
        "/guest – список гостей\n"
        "/addguest – добавить гостя\n"
        "/budget – бюджет свадьбы\n"
        "/addbudget – добавить расход/доход\n"
        "/reminders – напоминания\n"
        "/addreminder – добавить напоминание\n"
        "/place – адрес ЗАГСа и ресторана\n"
        "/info – информация для гостей"
    )

# ✅ Чек-лист
async def checklist_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply = "📋 Чек-лист:\n" + "\n".join(f"{i+1}. {item}" for i, item in enumerate(checklist))
    await update.message.reply_text(reply)

# 👥 Гости
async def guest_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not guests:
        await update.message.reply_text("Гости пока не добавлены.")
    else:
        msg = "👥 Список гостей:\n"
        for name, status in guests.items():
            emoji = "✅" if status == "подтвердил" else "❌"
            msg += f"{emoji} {name} — {status}\n"
        await update.message.reply_text(msg)

async def addguest_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Используй: /addguest Имя статус(подтвердил/нет)")
        return
    name = args[0]
    status = args[1].lower()
    if status not in ["подтвердил", "нет"]:
        await update.message.reply_text("Статус должен быть 'подтвердил' или 'нет'")
        return
    guests[name] = status
    await update.message.reply_text(f"Гость {name} добавлен со статусом: {status}")

# 💰 Бюджет
async def budget_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not budget:
        await update.message.reply_text("Бюджет пока пуст.")
        return
    msg = "💰 Бюджет:\n"
    total = 0
    for entry in budget:
        sign = "-" if entry["type"] == "расход" else "+"
        total += -entry["amount"] if entry["type"] == "расход" else entry["amount"]
        msg += f"{sign}{entry['amount']}₽ — {entry['note']}\n"
    msg += f"\nИтого: {total}₽"
    await update.message.reply_text(msg)

async def addbudget_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) < 3:
        await update.message.reply_text("Используй: /addbudget тип сумма описание\nнапример: /addbudget расход 5000 костюм")
        return
    b_type = args[0].lower()
    if b_type not in ["расход", "доход"]:
        await update.message.reply_text("Тип должен быть 'расход' или 'доход'")
        return
    try:
        amount = int(args[1])
    except ValueError:
        await update.message.reply_text("Сумма должна быть числом")
        return
    note = " ".join(args[2:])
    budget.append({"type": b_type, "amount": amount, "note": note})
    await update.message.reply_text(f"{b_type.capitalize()} {amount}₽ добавлен: {note}")

# 🔔 Напоминания
async def reminders_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not reminders:
        await update.message.reply_text("Напоминаний пока нет.")
    else:
        msg = "🔔 Напоминания:\n" + "\n".join(f"– {r}" for r in reminders)
        await update.message.reply_text(msg)

async def addreminder_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("Используй: /addreminder текст напоминания")
        return
    text = " ".join(args)
    reminders.append(text)
    await update.message.reply_text("🔔 Напоминание добавлено!")

# 📍 Адрес
async def place_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"📍 Адреса:\n\n"
        f"🏛️ ЗАГС: {zagc_address}\n"
        f"🍽️ Ресторан: {restaurant_address}"
    )

# 📄 Инфо для гостей
async def info_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎉 Информация для гостей:\n"
        "- Начало в 14:00 в ЗАГСе\n"
        "- После церемонии — банкет в ресторане\n"
        "- Просьба быть вовремя и с хорошим настроением 😊"
    )

# 🧠 Неизвестные команды
async def unknown_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Неизвестная команда. Введите /start чтобы увидеть список команд.")

# --- Основной запуск ---
def main():
    if not TOKEN:
        print("❌ Укажи TELEGRAM_TOKEN как переменную окружения.")
        return

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("checklist", checklist_cmd))
    app.add_handler(CommandHandler("guest", guest_cmd))
    app.add_handler(CommandHandler("addguest", addguest_cmd))
    app.add_handler(CommandHandler("budget", budget_cmd))
    app.add_handler(CommandHandler("addbudget", addbudget_cmd))
    app.add_handler(CommandHandler("reminders", reminders_cmd))
    app.add_handler(CommandHandler("addreminder", addreminder_cmd))
    app.add_handler(CommandHandler("place", place_cmd))
    app.add_handler(CommandHandler("info", info_cmd))
    app.add_handler(MessageHandler(filters.COMMAND, unknown_cmd))

    app.run_polling()

if __name__ == "__main__":
    main()
