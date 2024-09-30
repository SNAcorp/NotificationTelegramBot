import asyncio
import os

import redis.asyncio as redis
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InputFile
from aiohttp import web
from aiogram import types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from loguru import logger

logger.add("debug.log", format="{time} {level} {message}", level="DEBUG")

API_TOKEN = os.getenv('API_TOKEN')
REDIS_HOST = 'telegram-redis'  # Используем название сервиса из docker-compose
REDIS_PORT = 6379  # Порт Redis

# Инициализация бота и диспетчера с хранилищем FSM
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Подключение к Redis
redis_client = None

async def init_redis():
    global redis_client
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

# Кнопка для запроса номера телефона
contact_button = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Отправить номер телефона", request_contact=True)]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

# Обработчик команды /start
@dp.message(Command('start'))
async def send_welcome(message: Message, state: FSMContext):
    # Приветственное сообщение
    await message.answer(
        "Добро пожаловать! Пожалуйста, отправьте свой номер телефона, чтобы зарегистрироваться.",
        reply_markup=contact_button,
    )
# Обработчик получения контакта
@dp.message(lambda message: message.contact is not None)
async def handle_contact(message: types.Message, state: FSMContext):
    phone_number = message.contact.phone_number
    chat_id = message.chat.id
    logger.info(f"Received phone number: {phone_number}")
    # Сохраняем номер телефона и chat_id в Redis
    await redis_client.set(f"user:{phone_number}", chat_id)
    await message.answer("Ваш номер телефона зарегистрирован для получения сообщений!")

# Обработчик HTTP-запросов
async def handle_http_request(request):
    data = await request.json()
    message_text = data.get('message', 'Привет!')
    phone_number = data.get('phone_number')

    if not phone_number:
        return web.Response(text="Номер телефона не указан.", status=400)

    # Получаем chat_id по номеру телефона из Redis
    chat_id = await redis_client.get(f"user:{phone_number}")
    if chat_id:
        await bot.send_message(int(chat_id), message_text)
        return web.Response(text=f"Сообщение отправлено пользователю с номером {phone_number}.")
    else:
        return web.Response(text="Пользователь с данным номером телефона не найден.", status=404)

# Инициализация при старте
async def on_startup(app):
    asyncio.create_task(dp.start_polling(bot))
    await init_redis()  # Инициализируем подключение к Redis

# Создание веб-приложения Aiohttp
app = web.Application()
app.router.add_post('/send_message', handle_http_request)
app.on_startup.append(on_startup)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=8012)
