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
    "tycoons": {"name": "Тайкуны \U0001f3ea", "emoji": "\U0001f3ea", "games": [
        ("Restaurant Tycoon 2", "0000000001"),
        ("Theme Park Tycoon 2", "0000000002"),
        ("Retail Tycoon 2", "0000000003"),
        ("School Lunch Tycoon", "0000000004"),
        ("Pizza Factory Tycoon", "0000000005"),
        ("Car Wash Tycoon", "0000000006"),
        ("Airport Tycoon", "0000000007"),
        ("Theme Park Tycoon 1", "0000000008"),
        ("Aquatic Tycoon", "0000000009"),
        ("Mall Tycoon", "0000000010"),
    ]},
    "parkour": {"name": "Паркур \U0001f3c3", "emoji": "\U0001f3c3", "games": [
        ("Tower of Hell", "0000000011"),
        ("The Floor is Lava", "0000000012"),
        ("Escape Running Head", "0000000013"),
        ("Parkour", "0000000014"),
        ("Obby", "0000000015"),
        ("Hunger Games", "0000000016"),
        ("Super Bomb Survival", "0000000017"),
        ("Jailbreak Obby", "0000000018"),
        ("Mega Obby", "0000000019"),
        ("Tower Defense Simulator", "0000000020"),
    ]},
    "horror": {"name": "Хоррор \U0001f47b", "emoji": "\U0001f47b", "games": [
        ("Doors", "0000000021"),
        ("The Rake", "0000000022"),
        ("The Mimic", "0000000023"),
        ("Pressure", "0000000024"),
        ("Dead Silence", "0000000025"),
        ("Alone", "0000000026"),
        ("Finders Keepers", "0000000027"),
        ("The Intruder", "0000000028"),
        ("Grace", "0000000029"),
        ("The Night House", "0000000030"),
    ]},
    "puzzles": {"name": "Головоломки \U0001f9e9", "emoji": "\U0001f9e9", "games": [
        ("Natural Disaster Survival", "0000000031"),
        ("Escape Room", "0000000032"),
        ("Find the Markers", "0000000033"),
        ("The Maze", "0000000034"),
        ("Jailbreak Puzzle", "0000000035"),
        ("Simon Says", "0000000036"),
        ("Survive the Block", "0000000037"),
        ("Block Puzzle", "0000000038"),
        ("Treasure Hunt", "0000000039"),
        ("Murder Mystery 2", "0000000040"),
    ]},
    "fighting": {"name": "Драки \u2694\ufe0f", "emoji": "\u2694\ufe0f", "games": [
        ("Arsenal", "0000000041"),
        ("Bad Business", "0000000042"),
        ("Rivals", "0000000043"),
        ("Piggy", "0000000044"),
        ("The Strongest Battlegrounds", "0000000045"),
        ("Anime Fighters Simulator", "0000000046"),
        ("SFOTH IV", "0000000047"),
        ("Combat Warriors", "0000000048"),
        ("Blade Ball", "0000000049"),
        ("Sword Fight on Heights", "0000000050"),
    ]},
}

STATS_PATH = os.path.join(os.path.dirname(__file__), "stats.json")

LINK = "https://www.roblox.com/games/{}"

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
        ["Драки \u2694\ufe0f", "\U0001f3b2 Рандом"],
        ["\U0001f49c Поддержать"],
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

    if "\U0001f3ea" in text or "Тайкуны" in text:
        await show_genre(update, "tycoons")
    elif "\U0001f3c3" in text or "Паркур" in text:
        await show_genre(update, "parkour")
    elif "\U0001f47b" in text or "Хоррор" in text:
        await show_genre(update, "horror")
    elif "\U0001f9e9" in text or "Головоломки" in text:
        await show_genre(update, "puzzles")
    elif "\u2694" in text or "Драки" in text:
        await show_genre(update, "fighting")
    elif "Рандом" in text:
        await random_game(update)
    elif "Поддержать" in text:
        await donate_menu(update)
    else:
        await update.message.reply_text("Нажми кнопку внизу \U0001f447", reply_markup=main_menu())

def format_games(games):
    return "\n".join(f"\U0001f539 <a href='{LINK.format(id)}'>{name}</a>" for name, id in games)

async def show_genre(update, key):
    genre = GENRES[key]
    text = f"<b>{genre['emoji']} {genre['name']}</b>\n\n{format_games(genre['games'])}"
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=main_menu())

async def random_game(update: Update):
    genre_key = random.choice(list(GENRES.keys()))
    genre = GENRES[genre_key]
    name, id = random.choice(genre["games"])
    await update.message.reply_text(
        f"\U0001f3b2 <b>Рандом</b>\n\n"
        f"Жанр: {genre['emoji']} {genre['name']}\n"
        f"Игра: <a href='{LINK.format(id)}'>{name}</a>",
        parse_mode="HTML", reply_markup=main_menu()
    )

async def donate_menu(update: Update):
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("5 \u2b50", callback_data="don_5")],
        [InlineKeyboardButton("10 \u2b50", callback_data="don_10")],
        [InlineKeyboardButton("25 \u2b50", callback_data="don_25")],
        [InlineKeyboardButton("50 \u2b50", callback_data="don_50")],
    ])
    await update.message.reply_text(
        "\U0001f49c <b>Поддержать бота</b>\n\n"
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
        f"Ты отправил {amt} \u2b50",
        reply_markup=main_menu()
    )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    st = load_stats()
    count = len(st["donations"])
    total = st["total_donated"]
    last = st["donations"][-1] if st["donations"] else None
    text = f"\U0001f4ca <b>Статистика бота</b>\n\nВсего донатов: {count}\nВсего звёзд: {total}"
    if last:
        text += f"\nПоследний: {last['username']} — {last['amount']} \u2b50"
    await update.message.reply_text(text, parse_mode="HTML")

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
