import logging
import os
import random
import json
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
STARS_PRICE = 10

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

GENRES = {
    "horror": {"name": "Хоррор 👻", "games": [
        "Doors — https://www.roblox.com/games/0000000001",
        "The Rake — https://www.roblox.com/games/0000000002",
        "The Mimic — https://www.roblox.com/games/0000000003",
    ]},
    "parkour": {"name": "Паркур 🏃", "games": [
        "Tower of Hell — https://www.roblox.com/games/0000000004",
        "The Floor is Lava — https://www.roblox.com/games/0000000005",
        "Escape Running Head — https://www.roblox.com/games/0000000006",
    ]},
    "simulators": {"name": "Симуляторы 🏗", "games": [
        "Blox Fruits — https://www.roblox.com/games/0000000007",
        "Pet Simulator X — https://www.roblox.com/games/0000000008",
        "Mining Simulator 2 — https://www.roblox.com/games/0000000009",
    ]},
    "fighting": {"name": "Драки ⚔️", "games": [
        "Arsenal — https://www.roblox.com/games/0000000010",
        "Bad Business — https://www.roblox.com/games/0000000011",
        "Rivals — https://www.roblox.com/games/0000000012",
    ]},
}

ALL_GAMES = [game for g in GENRES.values() for game in g["games"]]

PREMIUM_FILE = "/data/premium.json"

def load_premium():
    if not os.path.exists(PREMIUM_FILE):
        return {}
    with open(PREMIUM_FILE) as f:
        return json.load(f)

def save_premium(db):
    os.makedirs(os.path.dirname(PREMIUM_FILE), exist_ok=True)
    with open(PREMIUM_FILE, "w") as f:
        json.dump(db, f)

def is_premium(user_id):
    db = load_premium()
    return db.get(str(user_id), False)

def set_premium(user_id):
    db = load_premium()
    db[str(user_id)] = True
    save_premium(db)

def main_menu():
    kb = [
        ["Хоррор 👻", "Паркур 🏃"],
        ["Симуляторы 🏗", "Драки ⚔️"],
        ["🎲 Случайный", "⭐ Премиум"],
    ]
    return ReplyKeyboardMarkup(kb, resize_keyboard=True)

def genre_keyboard():
    kb = [[InlineKeyboardButton(g["name"], callback_data=k)] for k, g in GENRES.items()]
    return InlineKeyboardMarkup(kb)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    status = "✅ Премиум" if is_premium(user.id) else "❌ Бесплатно"
    await update.message.reply_text(
        f"🎮 <b>Roblox Плейсы</b>\n\n"
        f"Привет, {user.first_name}!\n"
        f"Статус: {status}\n\n"
        "Выбери жанр кнопками внизу 👇",
        parse_mode="HTML",
        reply_markup=main_menu()
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    for key, genre in GENRES.items():
        if genre["name"].startswith(text.split()[0]):
            await show_genre(update, context, key)
            return

    if "Случайный" in text:
        name, link = random.choice(ALL_GAMES).split(" — ")
        await update.message.reply_text(f"🎲 <b>Случайный плейс:</b>\n\n{name}\n\n{link}", parse_mode="HTML", reply_markup=main_menu())
    elif "Премиум" in text:
        await donate(update, context)
    else:
        await update.message.reply_text("Нажми кнопку внизу 👇", reply_markup=main_menu())

async def show_genre(update, context, key):
    genre = GENRES[key]
    text = f"<b>{genre['name']}</b>\n\n" + "\n".join(f"• {g}" for g in genre["games"])
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=main_menu())

async def genre_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    genre = GENRES.get(query.data)
    if not genre:
        return
    text = f"<b>{genre['name']}</b>\n\n" + "\n".join(f"• {g}" for g in genre["games"])
    kb = [[InlineKeyboardButton("◀ Назад", callback_data="back")]]
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(kb))

async def back_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Выбери жанр 👇", reply_markup=genre_keyboard())

async def donate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if is_premium(user_id):
        await update.message.reply_text("✅ Уже премиум!", reply_markup=main_menu())
        return
    prices = [LabeledPrice(label="Премиум навсегда", amount=STARS_PRICE)]
    await context.bot.send_invoice(
        chat_id=update.effective_chat.id,
        title="Премиум-доступ",
        description="Премиум навсегда — никаких лимитов!",
        payload="premium",
        provider_token="",
        currency="XTR",
        prices=prices,
    )

async def pre_checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.pre_checkout_query.answer(ok=True)

async def payment_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    set_premium(user.id)
    await update.message.reply_text(f"🎉 Спасибо, {user.first_name}! Премиум активирован!", reply_markup=main_menu())

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(CallbackQueryHandler(genre_callback, pattern="^(horror|parkour|simulators|fighting)$"))
    app.add_handler(CallbackQueryHandler(back_callback, pattern="^back$"))
    app.add_handler(PreCheckoutQueryHandler(pre_checkout))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, payment_done))

    if RENDER_URL:
        logging.info(f"Запуск на Render: {RENDER_URL}")
        app.run_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN, webhook_url=f"{RENDER_URL}/{TOKEN}")
    else:
        logging.info("Запуск локально (polling)")
        app.run_polling()

if __name__ == "__main__":
    main()
