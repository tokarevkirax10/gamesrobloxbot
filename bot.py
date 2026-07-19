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

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

GENRES = {
    "tycoons": {"name": "Тайкуны 🏪", "games": [
        "Restaurant Tycoon 2 — https://www.roblox.com/games/0000000001",
        "Theme Park Tycoon 2 — https://www.roblox.com/games/0000000002",
        "Retail Tycoon 2 — https://www.roblox.com/games/0000000003",
    ]},
    "parkour": {"name": "Паркур 🏃", "games": [
        "Tower of Hell — https://www.roblox.com/games/0000000004",
        "The Floor is Lava — https://www.roblox.com/games/0000000005",
        "Escape Running Head — https://www.roblox.com/games/0000000006",
    ]},
    "horror": {"name": "Хоррор 👻", "games": [
        "Doors — https://www.roblox.com/games/0000000007",
        "The Rake — https://www.roblox.com/games/0000000008",
        "The Mimic — https://www.roblox.com/games/0000000009",
    ]},
    "puzzles": {"name": "Головоломки 🧩", "games": [
        "Natural Disaster Survival — https://www.roblox.com/games/0000000010",
        "Escape Room — https://www.roblox.com/games/0000000011",
        "Find the Markers — https://www.roblox.com/games/0000000012",
    ]},
}

ALL_GAMES = [game for g in GENRES.values() for game in g["games"]]

PREMIUM_PATH = "/data/premium.json"

def load_premium():
    if not os.path.exists(PREMIUM_PATH):
        return {}
    with open(PREMIUM_PATH) as f:
        return json.load(f)

def save_premium(db):
    os.makedirs(os.path.dirname(PREMIUM_PATH), exist_ok=True)
    with open(PREMIUM_PATH, "w") as f:
        json.dump(db, f)

def is_premium(user_id):
    return load_premium().get(str(user_id), False)

def set_premium(user_id):
    db = load_premium()
    db[str(user_id)] = True
    save_premium(db)

def main_menu():
    kb = [
        ["Тайкуны 🏪", "Паркур 🏃"],
        ["Хоррор 👻", "Головоломки 🧩"],
        ["🎲 Рандом", "⭐ Премиум"],
    ]
    return ReplyKeyboardMarkup(kb, resize_keyboard=True)

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
        await update.message.reply_text(f"🎲 <b>Рандом:</b>\n\n{name}\n\n{link}", parse_mode="HTML", reply_markup=main_menu())
    elif "Премиум" in text or "⭐" in text:
        await premium_menu(update)
    elif text.isdigit():
        await handle_donation_amount(update, context)
    else:
        await update.message.reply_text("Нажми кнопку внизу 👇", reply_markup=main_menu())

async def show_genre(update, key):
    genre = GENRES[key]
    text = f"<b>{genre['name']}</b>\n\n" + "\n".join(f"• {g}" for g in genre["games"])
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=main_menu())

async def premium_menu(update: Update):
    user_id = update.effective_user.id
    if is_premium(user_id):
        await update.message.reply_text("✅ У тебя уже есть премиум! Спасибо!", reply_markup=main_menu())
        return
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("💎 Купить премиум (10 ⭐)", callback_data="buy_premium")],
        [InlineKeyboardButton("💸 Поддержать (любая сумма)", callback_data="donate")],
    ])
    await update.message.reply_text(
        "⭐ <b>Премиум</b>\n\n"
        "Премиум навсегда — 10 Telegram Stars ⭐\n"
        "Можно просто поддержать бота любой суммой 💜",
        parse_mode="HTML", reply_markup=kb
    )

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "buy_premium":
        user_id = update.effective_user.id
        if is_premium(user_id):
            await query.edit_message_text("✅ Уже премиум!")
            return
        prices = [LabeledPrice("Премиум навсегда", 10)]
        await context.bot.send_invoice(
            chat_id=update.effective_chat.id,
            title="Премиум-доступ",
            description="Премиум навсегда — без ограничений!",
            payload="premium",
            provider_token="",
            currency="XTR",
            prices=prices,
        )

    elif query.data == "donate":
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("5 ⭐", callback_data="don_5")],
            [InlineKeyboardButton("10 ⭐", callback_data="don_10")],
            [InlineKeyboardButton("25 ⭐", callback_data="don_25")],
            [InlineKeyboardButton("50 ⭐", callback_data="don_50")],
            [InlineKeyboardButton("✏️ Другая сумма", callback_data="don_custom")],
        ])
        await query.edit_message_text("💸 Выбери сумму поддержки:", reply_markup=kb)

    elif query.data.startswith("don_"):
        amt = query.data.split("_")[1]
        if amt == "custom":
            await query.edit_message_text("✏️ Напиши число — сколько звёзд хочешь отправить:")
            context.user_data["awaiting_donation"] = True
            return
        prices = [LabeledPrice("Поддержка бота", int(amt))]
        await context.bot.send_invoice(
            chat_id=update.effective_chat.id,
            title="Поддержка бота",
            description="Спасибо за поддержку! 💜",
            payload=f"donation_{amt}",
            provider_token="",
            currency="XTR",
            prices=prices,
        )

async def handle_donation_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("awaiting_donation"):
        return await update.message.reply_text("Нажми кнопку внизу 👇", reply_markup=main_menu())
    try:
        amt = int(update.message.text)
        if amt < 1:
            raise ValueError
        context.user_data["awaiting_donation"] = False
        prices = [LabeledPrice("Поддержка бота", amt)]
        await context.bot.send_invoice(
            chat_id=update.effective_chat.id,
            title="Поддержка бота",
            description="Спасибо за поддержку! 💜",
            payload=f"donation_{amt}",
            provider_token="",
            currency="XTR",
            prices=prices,
        )
    except ValueError:
        await update.message.reply_text("Напиши целое число больше 0. Например: 15")

async def pre_checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.pre_checkout_query.answer(ok=True)

async def payment_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    payload = update.message.successful_payment.invoice_payload

    if payload == "premium":
        set_premium(user.id)
        await update.message.reply_text(
            f"🎉 Спасибо, {user.first_name}! Премиум активирован навсегда!",
            reply_markup=main_menu()
        )
    else:
        amt = update.message.successful_payment.total_amount
        await update.message.reply_text(
            f"💜 Спасибо за поддержку, {user.first_name}!\n"
            f"Ты отправил {amt} ⭐ — это очень помогает!",
            reply_markup=main_menu()
        )

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(PreCheckoutQueryHandler(pre_checkout))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, payment_done))

    if RENDER_URL:
        logging.info(f"Server on Render: {RENDER_URL}")
        app.run_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN, webhook_url=f"{RENDER_URL}/{TOKEN}")
    else:
        logging.info("Local polling mode")
        app.run_polling()

if __name__ == "__main__":
    main()
