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
        [InlineKeyboardButton(text="🎯 Фильтры", callback_data="filter")],
        [InlineKeyboardButton(text="🚀 Парсинг", callback_data="parse")]
    ])


def get_back_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back")]
    ])


def get_filter_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎯 По тегу", callback_data="tags")],
        [InlineKeyboardButton(text="📊 По сложности", callback_data="rating")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back")]
    ])


def get_tags_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💡 implementation", callback_data="tag:implementation")],
        [InlineKeyboardButton(text="🔢 math", callback_data="tag:math")],
        [InlineKeyboardButton(text="📊 graphs", callback_data="tag:graphs")],
        [InlineKeyboardButton(text="🎲 dp", callback_data="tag:dp")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back")]
    ])


def get_rating_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="800-1200", callback_data="rating:800-1200")],
        [InlineKeyboardButton(text="1200-1600", callback_data="rating:1200-1600")],
        [InlineKeyboardButton(text="1600-2000", callback_data="rating:1600-2000")],
        [InlineKeyboardButton(text="2000+", callback_data="rating:2000")],
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
            f"🔥 Div2D+: **{result[3] or 0}**",
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

        response_text = ""

        if not top:
            response_text = "📭 Пока нет задач с рейтингом"
        else:
            response_text = "🔥 **ТОП-10 сложных задач**\n\n"
            for i, (cf_id, name, rating, solved) in enumerate(top, 1):
                response_text += f"{i}. `{cf_id}` **{rating}**\n"
                response_text += f"   {name} ({solved or 0} solves)\n\n"

        await callback.message.edit_text(
            response_text + "\n*Нажмите ⬅️ Назад для меню*",
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
        f"🚀 **Парсинг запущен!**\nTask ID: `{task.id}`\n\nСкоро новые задачи!",
        reply_markup=get_back_menu(),
        parse_mode="Markdown"
    )


@dp.callback_query(F.data == "filter")
async def filter_menu(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "🎯 **Фильтры**\n\nВыберите фильтр:",
        reply_markup=get_filter_menu(),
        parse_mode="Markdown"
    )


@dp.callback_query(F.data == "tags")
async def tags_menu(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "🎯 **Популярные теги**\nВыберите:",
        reply_markup=get_tags_menu(),
        parse_mode="Markdown"
    )


@dp.callback_query(F.data == "rating")
async def rating_menu(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "📊 **Сложность**\nВыберите диапазон:",
        reply_markup=get_rating_menu(),
        parse_mode="Markdown"
    )


@dp.callback_query(F.data.startswith("tag:"))
async def tag_filter(callback: CallbackQuery):
    await callback.answer()
    tag = callback.data.split(":", 1)[1]
    db = SessionLocal()
    response_text = f"🔍 **Поиск по тегу: `{tag}`**\n\n"

    try:
        top = db.execute(text("""
            SELECT p.codeforces_id, p.name, p.rating, p.solved_count
            FROM problems p
            INNER JOIN problem_tags pt ON p.id = pt.problem_id
            WHERE pt.tag = :tag
            ORDER BY p.rating DESC NULLS LAST, p.id
            LIMIT 10
        """), {"tag": tag}).fetchall()

        tag_count = db.execute(text("""
            SELECT COUNT(*) FROM problem_tags WHERE tag = :tag
        """), {"tag": tag}).scalar() or 0

        response_text += f"📊 Задач с тегом: **{tag_count}**\n\n"

        if not top:
            response_text += "📭 Нет задач с рейтингом"
        else:
            response_text += "🎯 Топ задачи:\n\n"
            for i, (cf_id, name, rating, solved) in enumerate(top, 1):
                rating_str = f"**{rating}**" if rating else "❓"
                response_text += f"{i}. `{cf_id}` {rating_str}\n"
                response_text += f"   {name} ({solved or 0} solves)\n\n"

    except Exception as e:
        response_text += f"❌ `{str(e)[:80]}`"
    finally:
        db.close()

    await callback.message.edit_text(
        response_text + "\n*⬅️ Назад*",
        reply_markup=get_back_menu(),
        parse_mode="Markdown"
    )


@dp.callback_query(F.data.startswith("rating:"))
async def rating_filter(callback: CallbackQuery):
    await callback.answer()
    range_str = callback.data.split(":", 1)[1]
    db = SessionLocal()
    response_text = f"📈 **Сложность: {range_str}**\n\n"

    try:
        if "-" in range_str:
            min_r, max_r = map(int, range_str.split("-"))
            top = db.execute(text("""
                SELECT codeforces_id, name, rating, solved_count
                FROM problems 
                WHERE rating >= :min_r AND rating <= :max_r
                ORDER BY rating DESC LIMIT 10
            """), {"min_r": min_r, "max_r": max_r}).fetchall()
        else:
            min_r = int(range_str)
            top = db.execute(text("""
                SELECT codeforces_id, name, rating, solved_count
                FROM problems 
                WHERE rating >= :min_r
                ORDER BY rating DESC LIMIT 10
            """), {"min_r": min_r}).fetchall()

        if not top:
            response_text += "📭 Нет задач с рейтингом"
        else:
            response_text += f"🎯 Найдено {len(top)}:\n\n"
            for i, (cf_id, name, rating, solved) in enumerate(top, 1):
                response_text += f"{i}. `{cf_id}` **{rating}**\n"
                response_text += f"   {name}\n\n"

    except Exception:
        response_text += "❌ Ошибка"
    finally:
        db.close()

    await callback.message.edit_text(response_text + "\n*⬅️ Назад*",
                                     reply_markup=get_back_menu(),
                                     parse_mode="Markdown")


async def main():
    print("🤖 Telegram Bot запущен!")
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
