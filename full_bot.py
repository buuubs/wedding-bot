import logging
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# Вставь свой токен и ID сюда (или через set в командной строке)
TOKEN = os.getenv("TELEGRAM_TOKEN") or "8396815728:AAGXIPYdKF7oTSbP7-cEWXCSMP73ZvFnP0k"
OWNER_ID = int(os.getenv("OWNER_ID") or "123456789")

logging.basicConfig(level=logging.INFO)

# Данные
checklist = [
    "📆 Назначить дату свадьбы",
    "👗 Купить платье и костюм",
    "📜 Подать заявление в ЗАГС",
    "🏛️ Забронировать ресторан",
    "📷 Найти фотографа",
    "🎵 Выбрать музыку",
    "💌 Отправить приглашения",
    "💍 Купить кольца"
]

guests = {}
budget = []
reminders = []
zagc_address = "ул. Свадебная, 1"
restaurant_address = "пр. Любви, 5"

# Команды
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👰 Привет Ярослав Ксени  ! Я свадебный помощник.\n\n"
        "/checklist – чек-лист\n"
        "/guest – список гостей\n"
        "/addguest Имя статус\n"
        "/budget – бюджет\n"
        "/addbudget тип сумма описание\n"
        "/reminders – напоминания\n"
        "/addreminder текст\n"
        "/place – адреса\n"
        "/info – инфо для гостей"
    )

async def checklist_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "📋 Чек-лист:\n" + "\n".join(f"{i+1}. {item}" for i, item in enumerate(checklist))
    await update.message.reply_text(msg)

async def guest_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not guests:
        await update.message.reply_text("Гости пока не добавлены.")
        return
    text = "👥 Список гостей:\n"
    for name, status in guests.items():
        text += f"{name} — {status}\n"
    await update.message.reply_text(text)

async def addguest_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Пример: /addguest Игорь подтвердил")
        return
    guests[args[0]] = args[1]
    await update.message.reply_text("Гость добавлен!")

async def budget_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not budget:
        await update.message.reply_text("Бюджет пуст.")
        return
    total = 0
    msg = "💰 Бюджет:\n"
    for entry in budget:
        if entry['type'] == 'расход':
            total -= entry['amount']
        else:
            total += entry['amount']
        msg += f"{entry['type']}: {entry['amount']}₽ — {entry['note']}\n"
    msg += f"\nИтого: {total}₽"
    await update.message.reply_text(msg)

async def addbudget_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) < 3:
        await update.message.reply_text("Пример: /addbudget расход 5000 платье")
        return
    try:
        amount = int(args[1])
    except ValueError:
        await update.message.reply_text("Сумма должна быть числом.")
        return
    budget.append({"type": args[0], "amount": amount, "note": " ".join(args[2:])})
    await update.message.reply_text("Бюджет добавлен!")

async def reminders_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not reminders:
        await update.message.reply_text("Напоминаний нет.")
    else:
        await update.message.reply_text("\n".join(f"🔔 {r}" for r in reminders))

async def addreminder_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = " ".join(context.args)
    if not txt:
        await update.message.reply_text("Напиши текст напоминания.")
        return
    reminders.append(txt)
    await update.message.reply_text("Напоминание добавлено.")

async def place_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"🏛️ ЗАГС: {zagc_address}\n🍽️ Ресторан: {restaurant_address}"
    )

async def info_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📄 Инфо для гостей:\n"
        "- ЗАГС в 14:00\n"
        "- После — ресторан\n"
        "- Не забудьте подарки и улыбки 😊"
    )

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Не знаю такую команду. Напиши /start")

# Запуск
def main():
    if "ВСТАВЬ_СЮДА_ТОКЕН" in TOKEN:
        print("❌ Укажи токен в коде или через переменные среды!")
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
    app.add_handler(MessageHandler(filters.COMMAND, unknown))

    app.run_polling()

if __name__ == "__main__":
    main()
