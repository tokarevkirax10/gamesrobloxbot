import logging
import os
import random
import json
from datetime import datetime
from telegram import Update, LabeledPrice, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    PreCheckoutQueryHandler,
    CallbackQueryHandler,
    ContextTypes,
)

TOKEN = os.environ["BOT_TOKEN"]
PORT = int(os.environ.get("PORT", 8080))
RENDER_URL = os.environ.get("RENDER_EXTERNAL_URL")

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

GENRES = {
    "tycoons": {"name": "Тайкуны \U0001f3ea", "games": [
        "Restaurant Tycoon 2 — https://www.roblox.com/games/0000000001",
        "Theme Park Tycoon 2 — https://www.roblox.com/games/0000000002",
        "Retail Tycoon 2 — https://www.roblox.com/games/0000000003",
    ]},
    "parkour": {"name": "Паркур \U0001f3c3", "games": [
        "Tower of Hell — https://www.roblox.com/games/0000000004",
        "The Floor is Lava — https://www.roblox.com/games/0000000005",
        "Escape Running Head — https://www.roblox.com/games/0000000006",
    ]},
    "horror": {"name": "Хоррор \U0001f47b", "games": [
        "Doors — https://www.roblox.com/games/0000000007",
        "The Rake — https://www.roblox.com/games/0000000008",
        "The Mimic — https://www.roblox.com/games/0000000009",
    ]},
    "puzzles": {"name": "Головоломки \U0001f9e9", "games": [
        "Natural Disaster Survival — https://www.roblox.com/games/0000000010",
        "Escape Room — https://www.roblox.com/games/0000000011",
        "Find the Markers — https://www.roblox.com/games/0000000012",
    ]},
}

ALL_GAMES = [game for g in GENRES.values() for game in g["games"]]
STATS_PATH = os.path.join(os.path.dirname(__file__), "stats.json")

def load_stats():
    if not os.path.exists(STATS_PATH):
        return {"total_donated": 0, "donations": []}
    with open(STATS_PATH) as f:
        return json.load(f)

def save_stats(stats):
    with open(STATS_PATH, "w") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)

def main_menu():
    kb = [
        ["Тайкуны \U0001f3ea", "Паркур \U0001f3c3"],
        ["Хоррор \U0001f47b", "Головоломки \U0001f9e9"],
        ["\U0001f3b2 Рандом", "\U0001f49c Поддержать"],
    ]
    return ReplyKeyboardMarkup(kb, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"\U0001f3ae <b>Roblox Плейсы</b>\n\n"
        f"Привет, {user.first_name}!\n\n"
        "Выбирай жанр кнопками внизу \U0001f447",
        parse_mode="HTML",
        reply_markup=main_menu()
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if "Тайкуны" in text:
        await show_genre(update, "tycoons")
    elif "Паркур" in text:
        await show_genre(update, "parkour")
    elif "Хоррор" in text:
        await show_genre(update, "horror")
    elif "Головоломки" in text:
        await show_genre(update, "puzzles")
    elif "Рандом" in text:
        name, link = random.choice(ALL_GAMES).split(" — ")
        await update.message.reply_text(
            f"\U0001f3b2 <b>Рандом:</b>\n\n{name}\n\n{link}",
            parse_mode="HTML", reply_markup=main_menu()
        )
    elif "Поддержать" in text:
        await donate_menu(update)
    else:
        await update.message.reply_text("Нажми кнопку внизу \U0001f447", reply_markup=main_menu())

async def show_genre(update, key):
    genre = GENRES[key]
    text = f"<b>{genre['name']}</b>\n\n" + "\n".join(f"• {g}" for g in genre["games"])
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=main_menu())

async def donate_menu(update: Update):
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("5 ⭐", callback_data="don_5")],
        [InlineKeyboardButton("10 ⭐", callback_data="don_10")],
        [InlineKeyboardButton("25 ⭐", callback_data="don_25")],
        [InlineKeyboardButton("50 ⭐", callback_data="don_50")],
    ])
    await update.message.reply_text(
        "\U0001f4b8 <b>Поддержать бота</b>\n\n"
        "Бот полностью бесплатный \U0001f49c\n"
        "Если хочешь поддержать — выбери сумму \U0001f447\n\n"
        "Звёзды помогут боту жить дальше \u2601\ufe0f",
        parse_mode="HTML", reply_markup=kb
    )

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("don_"):
        amt = int(query.data.split("_")[1])
        prices = [LabeledPrice("Поддержка бота", amt)]
        await context.bot.send_invoice(
            chat_id=update.effective_chat.id,
            title="Поддержка бота",
            description="Спасибо! \U0001f49c",
            payload=f"donation_{amt}",
            provider_token="",
            currency="XTR",
            prices=prices,
        )

async def pre_checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.pre_checkout_query.answer(ok=True)

async def payment_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    amt = update.message.successful_payment.total_amount

    stats = load_stats()
    stats["total_donated"] += amt
    stats["donations"].append({
        "user_id": user.id,
        "username": user.username or user.first_name,
        "amount": amt,
        "date": datetime.now().isoformat(),
    })
    save_stats(stats)

    await update.message.reply_text(
        f"\U0001f49c Спасибо, {user.first_name}!\n"
        f"Ты отправил {amt} \u2b50 — это очень помогает!",
        reply_markup=main_menu()
    )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stats = load_stats()
    total = stats["total_donated"]
    count = len(stats["donations"])
    await update.message.reply_text(
        f"\U0001f4ca <b>Статистика бота</b>\n\n"
        f"Всего донатов: {count}\n"
        f"Всего звёзд: {total} \u2b50\n"
        f"Последний: {stats['donations'][-1]['username'] if stats['donations'] else '—'}",
        parse_mode="HTML"
    )

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(PreCheckoutQueryHandler(pre_checkout))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, payment_done))

    if RENDER_URL:
        app.run_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN, webhook_url=f"{RENDER_URL}/{TOKEN}")
    else:
        app.run_polling()

if __name__ == "__main__":
    main()
