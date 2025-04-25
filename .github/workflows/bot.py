import asyncio
import random
import aiosqlite
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = "7661568375:AAHo-gAwHd1c2eTNp08spmteYrxgDbCK4ic"
DB_PATH = "game_data.db"

# --- Инициализация БД ---
async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                name TEXT,
                balance INTEGER DEFAULT 0,
                games_played INTEGER DEFAULT 0,
                last_bonus TEXT
            )
        """)
        await db.commit()

# --- Регистрация игрока ---
async def register_user(user):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR IGNORE INTO users (user_id, name) VALUES (?, ?)", (user.id, user.first_name))
        await db.commit()

# --- Команда /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await register_user(user)

    keyboard = [
        [InlineKeyboardButton("🎁 Бонус", callback_data="bonus")],
        [InlineKeyboardButton("🎮 Играть", callback_data="game")],
        [InlineKeyboardButton("👤 Профиль", callback_data="profile")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(f"Привет, {user.first_name}! Я игровой бот 🎮", reply_markup=reply_markup)

# --- Обработчик кнопок ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    await query.answer()
    await register_user(user)

    async with aiosqlite.connect(DB_PATH) as db:
        if query.data == "bonus":
            row = await db.execute_fetchone("SELECT last_bonus, balance FROM users WHERE user_id = ?", (user.id,))
            now = datetime.now()
            last_bonus = datetime.fromisoformat(row[0]) if row[0] else now - timedelta(days=1)

            if now - last_bonus >= timedelta(hours=24):
                await db.execute("UPDATE users SET balance = balance + 10, last_bonus = ? WHERE user_id = ?", (now.isoformat(), user.id))
                await db.commit()
                await query.edit_message_text("🎁 Вы получили 10 монет!")
            else:
                hours = (timedelta(hours=24) - (now - last_bonus)).seconds // 3600
                await query.edit_message_text(f"🔄 Бонус доступен через {hours} ч.")

        elif query.data == "profile":
            row = await db.execute_fetchone("SELECT name, balance, games_played FROM users WHERE user_id = ?", (user.id,))
            if row:
                name, balance, games = row
                achievements = []
                if games >= 5:
                    achievements.append("🏆 Геймер")
                if balance >= 50:
                    achievements.append("💰 Богач")
                ach = "\n".join(achievements) if achievements else "Нет достижений"

                await query.edit_message_text(f"👤 {name}\n💰 Баланс: {balance} монет\n🎮 Игр сыграно: {games}\n🏅 Достижения:\n{ach}")

        elif query.data == "game":
            number = random.randint(1, 5)
            context.user_data["target"] = number
            await query.edit_message_text("Я загадал число от 1 до 5. Введи /guess <число>")

# --- Угадай число ---
async def guess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if "target" not in context.user_data:
        await update.message.reply_text("❌ Сначала нажмите '🎮 Играть'.")
        return

    try:
        guess = int(context.args[0])
    except:
        await update.message.reply_text("⚠ Введите число: /guess 3")
        return

    target = context.user_data.pop("target")
    async with aiosqlite.connect(DB_PATH) as db:
        if guess == target:
            await db.execute("UPDATE users SET balance = balance + 5, games_played = games_played + 1 WHERE user_id = ?", (user_id,))
USER.ID - Ihr Medien-Login
USER.ID - Ihr Medien-Login
user.id
10:30


await db.commit()
            await update.message.reply_text("🎉 Верно! +5 монет.")
        else:
            await db.execute("UPDATE users SET games_played = games_played + 1 WHERE user_id = ?", (user_id,))
            await db.commit()
            await update.message.reply_text(f"❌ Неправильно. Было число {target}.")

# --- Запуск ---
async def main():
    await init_db()
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("guess", guess))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("✅ Бот запущен!")
    await app.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
