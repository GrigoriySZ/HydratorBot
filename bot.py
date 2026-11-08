import asyncio
import logging
from os import getenv
from dotenv import load_dotenv
from datetime import date

from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command
from aiogram.types import (
    Message, ReplyKeyboardMarkup, KeyboardButton,
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
            [KeyboardButton(text=BTN_PROGRESS),
            KeyboardButton(text=BTN_RESET)]
        ],
        resize_keyboard=True,
        input_field_placeholder='Выберите действите из меню'
    )
    return keyboard

# Обработчики команд
@router.message(Command("start"))
async def start_handler(message: Message):
    await message.answer(
        text='Привет! Я бот "Гидратор" 💧\n\n' \
        'Я помогу тебе отследить количество выпитой воды за день\n' \
        'Каждый выпитый стакан - это ещё 250 мл к твоей цели!',
        reply_markup=get_main_keyboard()
    )

@router.message(F.text == BTN_ADD)
async def add_water_handler(message: Message):
    """ Добавляет 250 мл воды к счетчику выпитой воды пользователем """

    telegram_user_id = message.from_user.id
    user_data = get_user_data(telegram_user_id)

    user_data["amount"] += GLASS_AMOUNT

    await message.answer(
        'Отлично! 🥤 Выпитый стакан записан!\n'
        f'Итого: {user_data["amount"]} мл'
    )

@router.message(F.text == BTN_PROGRESS)
async def progress_handler(message: Message):
    """ Выводит пользователю его статистику потребления воды за день """

    telegram_user_id = message.from_user.id
    user_data = get_user_data(telegram_user_id)

    amount = user_data["amount"]
    glass_count = amount / GLASS_AMOUNT
    remaining = max(0, DAILY_GOAL - amount)
    percentage = amount / DAILY_GOAL * 100

    response = (
        '📊 Твой прогресс за сегодня: \n\n'
        f'💧 Выпито: {amount} мл. или {glass_count:.0f} стаканов\n'
        f'🎯 Дневная цель: {DAILY_GOAL} мл\n'
        f'📈 Выполнено: {percentage:.0f}%\n'
    )

    if amount > DAILY_GOAL:
        response += (
            '\n🎉 Поздравляю! Дневная цель превышена\n'
            'Отличная работа! 🏆'
        )
    elif amount == DAILY_GOAL:
        response += (
            '\n 🎉 Отлично! Дневная цель достигнута'
        )
    else:
        response += (
            f'\n🥤 Осталось выпить: {remaining} мл'
        )

    await message.answer(response)

@router.message(F.text == BTN_RESET)
async def reset_handler(message: Message):
    """ Сбрасывает счетчик выпитой пользователем воды """

    telegram_user_id = message.from_user.id
    user_data = get_user_data(telegram_user_id)

    user_data["amount"] = 0

    await message.answer(
        '🔄️ Счетчик сброшен!\n'
        'Начинаем отслеживать потребление заново 💧'
    )

@router.message()
async def unknown_handler(message: Message):
    await message.answer(
        'Я пока понимаю только кнопки меню 👽\n\n'
        'Пожалуйста, выбери нужное действите 👇'
    )

# Главная функция
async def main():
    """ Запуск процесса поллинга """
    if not BOT_TOKEN:
        raise ValueError('Не найден BOT_TOKEN в файле .env')

    logger = logging.getLogger(__name__)

    logger.info('Бот готов к работе')

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main())