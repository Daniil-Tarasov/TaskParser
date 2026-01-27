from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from aiogram.types import InlineKeyboardMarkup

from src.bot import (
    SearchStates,
    filter_menu,
    get_back_menu,
    get_filter_menu,
    get_main_menu,
    parse_callback,
    process_search,
    rating_filter,
    rating_menu,
    search_command,
    start,
    stats_callback,
    tag_filter,
    tags_menu,
    top_callback,
)


class TestBotKeyboards:
    """Клавиатуры"""

    def test_get_main_menu(self):
        kb = get_main_menu()
        assert isinstance(kb, InlineKeyboardMarkup)
        assert len(kb.inline_keyboard) == 5
        assert any("📊 Статистика" in btn.text for row in kb.inline_keyboard for btn in row)

    def test_get_back_menu(self):
        kb = get_back_menu()
        assert any("⬅️ Назад" in btn.text for row in kb.inline_keyboard for btn in row)

    def test_get_filter_menu(self):
        kb = get_filter_menu()
        assert any("🎯 По тегу" in btn.text for row in kb.inline_keyboard for btn in row)


@pytest_asyncio.fixture
async def message_mock():
    message = AsyncMock()
    message.text = "2185A"
    message.answer = AsyncMock()
    return message


@pytest_asyncio.fixture
async def callback_mock():
    callback = AsyncMock()
    callback.answer = AsyncMock()
    callback.message.edit_text = AsyncMock()
    callback.data = "stats"
    return callback


@pytest_asyncio.fixture
async def state_mock():
    state = MagicMock()
    state.set_state = AsyncMock()
    state.clear = AsyncMock()
    return state


class TestBotHandlers:
    """Основные handlers"""

    @pytest.mark.asyncio
    @patch("src.bot.SessionLocal")
    async def test_start_handler(self, mock_db, message_mock):
        await start(message_mock)
        message_mock.answer.assert_called_once()

    @pytest.mark.asyncio
    @patch("src.bot.SessionLocal")
    async def test_stats_callback(self, mock_db, callback_mock):
        mock_session = MagicMock()
        mock_db.return_value = mock_session
        mock_session.execute.return_value.fetchone.return_value = (100, 80, 1500, 20)

        await stats_callback(callback_mock)
        callback_mock.answer.assert_called_once()

    @pytest.mark.asyncio
    @patch("src.bot.app")
    async def test_parse_callback(self, mock_celery, callback_mock):
        mock_celery.send_task.return_value.id = "test-task-id"
        await parse_callback(callback_mock)
        callback_mock.answer.assert_called_once()

    @pytest.mark.asyncio
    @patch("src.bot.SessionLocal")
    async def test_top_callback(self, mock_db, callback_mock):
        mock_session = MagicMock()
        mock_db.return_value = mock_session
        mock_session.execute.return_value.fetchall.return_value = [("2185A", "Test", 1200, 100)]
        await top_callback(callback_mock)
        callback_mock.answer.assert_called_once()

    @pytest.mark.asyncio
    @patch("src.bot.SessionLocal")
    async def test_process_search_found(self, mock_db, message_mock, state_mock):
        mock_session = MagicMock()
        mock_db.return_value = mock_session
        mock_session.execute.return_value.fetchone.return_value = (
            "2185A",
            "Perfect Root",
            1200,
            30850,
            "A",
            "Round 987",
        )
        await process_search(message_mock, state_mock)
        message_mock.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_command(self, message_mock, state_mock):
        """Команда /search"""

        await search_command(message_mock, state_mock)
        state_mock.set_state.assert_called_once_with(SearchStates.waiting_code)  # ✅ ТОЧНЫЙ аргумент!
        message_mock.answer.assert_called_once()


class TestBotMenus:
    """Меню callbacks"""

    @pytest.mark.asyncio
    async def test_filter_menu(self, callback_mock):
        await filter_menu(callback_mock)
        callback_mock.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_tags_menu(self, callback_mock):
        callback_mock.data = "tags"
        await tags_menu(callback_mock)
        callback_mock.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_rating_menu(self, callback_mock):
        callback_mock.data = "rating"
        await rating_menu(callback_mock)
        callback_mock.answer.assert_called_once()


class TestBotFilters:
    """Фильтры"""

    @pytest.mark.asyncio
    @patch("src.bot.SessionLocal")
    async def test_tag_filter(self, mock_db, callback_mock):
        mock_session = MagicMock()
        mock_db.return_value = mock_session
        mock_session.execute.return_value.fetchall.return_value = [("2185A", "Test", 1200, 100)]
        callback_mock.data = "tag:math"
        await tag_filter(callback_mock)
        callback_mock.answer.assert_called_once()

    @pytest.mark.asyncio
    @patch("src.bot.SessionLocal")
    async def test_rating_filter(self, mock_db, callback_mock):
        mock_session = MagicMock()
        mock_db.return_value = mock_session
        mock_session.execute.return_value.fetchall.return_value = [("2191B", "Test", 1800, 1500)]
        callback_mock.data = "rating:1600-2000"
        await rating_filter(callback_mock)
        callback_mock.answer.assert_called_once()


class TestBotStates:
    """FSM состояния"""

    def test_search_states(self):
        """Проверка SearchStates"""

        assert hasattr(SearchStates, "waiting_code")
        state = SearchStates.waiting_code

        assert state.state == "SearchStates:waiting_code"
        assert "SearchStates:waiting_code" in str(state)
        assert repr(state).startswith("<State")
