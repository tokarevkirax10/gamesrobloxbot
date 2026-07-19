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
ADMIN_ID = 766347597

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

S = "https://www.roblox.com/share?code={}&type=ExperienceDetails&stamp=1"
ZO = "https://ro.blox.com/Ebh5?pid=share&is_retargeting=true&af_dp=roblox%3A%2F%2Fnavigation%2Fgame_details%3FgameId%3D9351808693&af_web_dp=https%3A%2F%2Fwww.roblox.com%2Fgames%2F72811796045029"

GENRES = {
    "tycoons": {"name": "Тайкуны \U0001f3ea", "emoji": "\U0001f3ea", "games": [
        ("Restaurant Tycoon 2", S.format("b8fe46679efd1140b5ea8b0a04a6b21d")),
        ("Retail Tycoon 2", S.format("daea237eb0d1c646b125dea6e1598926")),
        ("Theme Park Tycoon 2", S.format("95a1f7ea771f674ca2e36101f242074f")),
        ("Lumber Tycoon 2", S.format("aeef0f294d695e4bbd1ea87ddfedeff4")),
        ("Car Dealership Tycoon", S.format("1ce98361b37a19418d7826278e25de05")),
        ("My Restaurant", S.format("5825bb1c77b3554badafb6cca5d5ff4c")),
        ("Airport Tycoon", S.format("7858b2d226c6d943a0bcecaef7cd1fac")),
        ("Hospital Tycoon", S.format("f65ce61b06e1234698c9777e27588673")),
        ("Aquarium Tycoon", S.format("9751b90d5d444c40b25942cc55379980")),
        ("Your Zoo", ZO),
    ]},
    "parkour": {"name": "Паркур \U0001f3c3", "emoji": "\U0001f3c3", "games": [
        ("Tower of Hell", S.format("20ee7cba5d22e5408e6142c2365e6567")),
        ("Flood Escape 2", S.format("8f0cc960daf1af4e9d6cfc10735d5386")),
        ("Mega Fun Obby", S.format("c95cdc7635391f488decf79cb0919ea0")),
        ("Parkour Run", S.format("83ffc6cedefa3343bab51a81fd90345a")),
        ("Troll Obby", S.format("d5745a12a440594187b1f39266396ac0")),
        ("Tower Defense Simulator", S.format("d1ef2bc7c48e3846a06f88833415298a")),
        ("Super Bomb Survival", S.format("2df224cf32cba04381203e0692bec1b6")),
        ("Omega Obby", S.format("0a4911b1f66d6241a4ad3ad1a56a6c54")),
        ("Untitled Parkour Game", S.format("5560adf83b162b4aba47884b3b2976a1")),
        ("STEEP STEPS", S.format("b455031aefdc4e4898d6b2460a45c2ba")),
    ]},
    "horror": {"name": "Хоррор \U0001f47b", "emoji": "\U0001f47b", "games": [
        ("Doors", S.format("29d4c511e035c04482e3fa53ace32501")),
        ("The Rake", S.format("009191bd982a4c448a6a2ebba34e3baf")),
        ("The Mimic", S.format("cfe7cded18ffa040b6a9c56a546a9551")),
        ("Pressure", S.format("a2fb30a9fa09e442a223354637304923")),
        ("Dead Silence", S.format("39ad47a381ae98448cb17db53184a4fd")),
        ("Alone", S.format("a567ee68104c54478b3ffe4adbdf7106")),
        ("Finders Keepers", S.format("697e1a50b6b1a743aaac429cfe6e5e0d")),
        ("The Intruder", S.format("56a22df944028242b94e91852a170cfa")),
        ("The Cultist", S.format("aa9345a6c57ba04c89d136fbc6aca648")),
        ("Stifled Fears (Voice)", S.format("6e3faf9a2099fc4388c9ba078b4a933b")),
    ]},
    "puzzles": {"name": "Головоломки \U0001f9e9", "emoji": "\U0001f9e9", "games": [
        ("Apeirophobia", S.format("05844940775811469fea443191112be4")),
        ("Escape Room", S.format("958128a9e901b447b1e7e9e6d4738dea")),
        ("Teamwork Puzzles 2", S.format("341a2f2aef8aaf4c8390f5fbf75f3954")),
        ("Find The Markers", S.format("28cc46d6a5694b4a93f87cf8cc545cac")),
        ("Color or Die", S.format("5c531e07d0d3e04e9e44b737504ac685")),
        ("Cheese Escape", S.format("cfc2a121ab7050479e395f652d0c68af")),
        ("Treasure Hunt", S.format("cf1dd38483209346a600f955e54c8c35")),
        ("Block Puzzle", S.format("1d60ccdee6d42c47ae861c479662a030")),
        ("The Maze", S.format("d7977219896e5c4bb8e966fd7765d4e2")),
        ("Simon Says", S.format("0c1522f44eab7e4fa24ce93eed75fdcb")),
    ]},
    "fighting": {"name": "Драки \u2694\ufe0f", "emoji": "\u2694\ufe0f", "games": [
        ("Combat Warriors", S.format("cc5fa6f7738c654d8718c5533c45acfd")),
        ("The Strongest Battlegrounds", S.format("4fdd9d9933bd6642b07b604257ea4d38")),
        ("Untitled Boxing Game", S.format("88f04f983728834493574267e97a27be")),
        ("Heroes Battlegrounds", S.format("cd5785fbbce45d45910d8cdcfe848292")),
        ("Elemental Battlegrounds", S.format("6c554fbf12c18b40878ec871362287de")),
        ("Jujutsu Shenanigans", S.format("c781ef79f4033a40984cabbfc92fe1da")),
        ("Super Doomspire", S.format("3848f2720f63154ba6396afc60ed3a90")),
        ("Project Smash", S.format("f44fc9c95f043e48b83da8d1d4cbf6d3")),
        ("Blox Fruits", S.format("c58470844894254c91ae8505b9e5a211")),
        ("Deepwoken", S.format("64d1e6955775e2408d0df82e7825b68f")),
    ]},
}

STATS_PATH = os.path.join(os.path.dirname(__file__), "stats.json")
USERS_PATH = os.path.join(os.path.dirname(__file__), "users.json")

LINK = "https://www.roblox.com/games/{}"

def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path) as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_stats():
    return load_json(STATS_PATH, {"total_donated": 0, "donations": []})

def save_stats(stats):
    save_json(STATS_PATH, stats)

def save_user(user):
    users = load_json(USERS_PATH, [])
    existing = next((u for u in users if u["id"] == user.id), None)
    now = datetime.now().isoformat()
    if existing:
        existing["last_active"] = now
    else:
        users.append({
            "id": user.id,
            "username": user.username or None,
            "name": user.first_name,
            "date": now,
            "last_active": now,
        })
    save_json(USERS_PATH, users)

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
    save_user(user)
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
    return "\n".join(f"\U0001f539 <a href='{url}'>{name}</a>" for name, url in games)

async def show_genre(update, key):
    genre = GENRES[key]
    text = f"<b>{genre['emoji']} {genre['name']}</b>\n\n{format_games(genre['games'])}"
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=main_menu())

async def random_game(update: Update):
    genre_key = random.choice(list(GENRES.keys()))
    genre = GENRES[genre_key]
    name, url = random.choice(genre["games"])
    await update.message.reply_text(
        f"\U0001f3b2 <b>Рандом</b>\n\n"
        f"Жанр: {genre['emoji']} {genre['name']}\n"
        f"Игра: <a href='{url}'>{name}</a>",
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

def count_recent(users, field, hours=24):
    from datetime import timedelta
    cutoff = datetime.now() - timedelta(hours=hours)
    return sum(1 for u in users if u.get(field) and datetime.fromisoformat(u[field]) >= cutoff)

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Команда только для админа")
        return
    st = load_stats()
    users = load_json(USERS_PATH, [])
    don_count = len(st["donations"])
    total = st["total_donated"]
    last = st["donations"][-1] if st["donations"] else None
    new_24h = count_recent(users, "date")
    active_24h = count_recent(users, "last_active")
    text = (
        f"\U0001f4ca <b>Статистика бота</b>\n\n"
        f"Всего пользователей: {len(users)}\n"
        f"Новых за 24ч: {new_24h}\n"
        f"Активных за 24ч: {active_24h}\n"
        f"Донатов: {don_count}\n"
        f"Всего звёзд: {total}"
    )
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
