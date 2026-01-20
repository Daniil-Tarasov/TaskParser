import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from sqlalchemy import text
from dotenv import load_dotenv
from src.database import SessionLocal
from src.celery_app import app

load_dotenv()
logging.basicConfig(level=logging.INFO)
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


def get_main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статистика", callback_data="stats")],
        [InlineKeyboardButton(text="🔥 Топ задач", callback_data="top")],
        [InlineKeyboardButton(text="🚀 Парсинг", callback_data="parse")]
    ])


def get_back_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back")]
    ])


@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "🚀 **Codeforces Task Parser Bot**\n\n"
        "Система работает! 20 задач в БД!\n\n"
        "Выберите действие:",
        reply_markup=get_main_menu(),
        parse_mode="Markdown"
    )


@dp.callback_query(F.data == "back")
async def back_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "🚀 **Codeforces Task Parser Bot**\n\n"
        "Система работает! 20 задач в БД!\n\n"
        "Выберите действие:",
        reply_markup=get_main_menu(),
        parse_mode="Markdown"
    )


@dp.callback_query(F.data == "stats")
async def stats_callback(callback: CallbackQuery):
    await callback.answer()
    db = SessionLocal()
    try:
        result = db.execute(text("""
            SELECT 
                COUNT(*) as total,
                COUNT(rating) as rated,
                ROUND(AVG(rating)::numeric, 0) as avg_rating,
                COUNT(*) FILTER (WHERE rating >= 2000) as hard
            FROM problems
        """)).fetchone()

        await callback.message.edit_text(
            f"📊 **Статистика**\n\n"
            f"📈 Всего задач: **{result[0]}**\n"
            f"⭐ С рейтингом: **{result[1]}**\n"
            f"📊 Средний рейтинг: **{result[2] or 0}**\n"
            f"🔥 Div2D+: **{result[3] or 0}**\n\n"
            f"_Нажмите ⬅️ Назад для меню_",
            reply_markup=get_back_menu(),
            parse_mode="Markdown"
        )
    finally:
        db.close()


@dp.callback_query(F.data == "top")
async def top_callback(callback: CallbackQuery):
    await callback.answer()
    db = SessionLocal()
    try:
        top = db.execute(text("""
            SELECT codeforces_id, name, rating, solved_count
            FROM problems 
            WHERE rating IS NOT NULL
            ORDER BY rating DESC 
            LIMIT 10
        """)).fetchall()

        if not top:
            response_text = "📭 Пока нет задач с рейтингом"
        else:
            response_text = "🔥 **ТОП-10 сложных задач**\n\n"
            for i, (cf_id, name, rating, solved) in enumerate(top, 1):
                response_text += f"{i}. `{cf_id}` **{rating}**\n"
                response_text += f"   {name} ({solved or 0} solves)\n\n"

        await callback.message.edit_text(
            response_text + "\n_Нажмите ⬅️ Назад для меню_",
            reply_markup=get_back_menu(),
            parse_mode="Markdown"
        )
    finally:
        db.close()


@dp.callback_query(F.data == "parse")
async def parse_callback(callback: CallbackQuery):
    await callback.answer()
    task = app.send_task('src.tasks.parse_problems', args=[100])
    await callback.message.edit_text(
        f"🚀 **Парсинг запущен!**\nTask ID: `{task.id}`\n\n"
        f"Скоро новые задачи!\n\n"
        f"_Нажмите ⬅️ Назад для меню_",
        reply_markup=get_back_menu(),
        parse_mode="Markdown"
    )


async def main():
    print("🤖 Telegram Bot запущен!")
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
