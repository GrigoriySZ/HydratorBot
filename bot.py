import asyncio
import logging
from os import getenv
from dotenv import load_dotenv
from datetime import date

from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    Message, ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Загружаем переменные окружения
load_dotenv()
BOT_TOKEN = getenv("BOT_TOKEN")

# Константы 
GLASS_AMOUNT = 250
DAILY_GOAL = 2000

BTN_ADD = '🥤 Выпил стакан (250 мл)'
BTN_PROGRESS = '📊 Мой прогресс'
BTN_RESET = '🔄 Сброс'

# Временное хранилище
# Формат хранилища: {"user_id": {"date": date, "amount": int}, }
users_data = {}

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

router = Router()
dp.include_router(router)

# Клавиатура
MENU_BTNS = {BTN_ADD, BTN_PROGRESS, BTN_RESET}

# Получаем данные пользователя c 
def get_user_data(user_id: int) -> dict:
    """ Получить данные пользователя с идентификатором user_id"""

    today = date.today()

    if user_id not in users_data:
        users_data[user_id] = {
            "date": today,
            "amount": 0
        }

    # Обновляем счетчик для нового дня
    elif users_data[user_id]["date"] != today:
        users_data[user_id] = {
            "date": today,
            "amount": 0
        }

    return users_data[user_id]

def get_main_keyboard() -> ReplyKeyboardMarkup:
    """ Получить клавиатуру с основными функциональными клавишами """

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_ADD)],
            [KeyboardButton(text=BTN_PROGRESS)],
            [KeyboardButton(text=BTN_RESET)]
        ],
        resize_keyboard=True,
        input_field_placeholder='Выберите действите из меню'
    )
    return keyboard

@router.message(Command('start'))
async def cmd_start(message: Message):
    await message.answer(
        text='Привет! Я бот "Гидратор" 💧\n\n' \
        'Я помогу тебе отследить количество выпитой воды за день\n' \
        'Каждый выпитый стакан - это ещё 250 мл к твоей цели!',
        reply_markup=get_main_keyboard()
    )

async def main():
    """ Запуск процесса поллинга """
    logger = logging.getLogger(__name__)

    logger.info('Бот готов к работе')

    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())