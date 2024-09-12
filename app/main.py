import telebot
import threading
import uvicorn
import time
from fastapi import (FastAPI, Depends, HTTPException, Request)
from fastapi.middleware.cors import (CORSMiddleware)
from fastapi.staticfiles import (StaticFiles)

#from app.logging_config import log

app = FastAPI()

'''
@app.on_event("startup")
async def startup():
    log.bind(type="app").info("Application start up")
'''

origins = [
    "http://localhost",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TOKEN = "6874495766:AAGyocvfJ-DzaqDQfhMe7L7BeEzlG55S1lM"
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=["start"])
def start_command(message, res=False):
    args = message.text.split()

    if len(args) > 1:
        token = args[1]
        bot.send_message(message.chat.id, f"Ваш токен: {token}")
    else:
        bot.send_message(message.chat.id, "Пожалуйста, передайте токен.")


#POST-ЗАПРОС НА LOCALHOST 80
# TG-ID,
@bot.message_handler(content_types=["text"])
def handle_text(message):
    bot.send_message(message.chat.id, 'Ваш токен на проверке...')


@app.post("/send_message")
async def send_message(request: Request):
    
    data = await request.json()
    chat_id = data["telegram_id"]
    message_text = data["message"]
    
    # Отправляем сообщение с помощью функции
    send_message_by_chat_id(chat_id, message_text)
    
    return {"status": "success"}


# Функция для отправки сообщения по chat_id
def send_message_by_chat_id(chat_id, message_text):
    try:
        bot.send_message(chat_id, message_text)
        print(f"Сообщение успешно отправлено в чат {chat_id}")
    except Exception as e:
        print(f"Ошибка при отправке сообщения в чат {chat_id}: {e}")




#ФУНКЦИЯ ДЛЯ ПРОВЕРКИ ТОКЕНА (НУЖНО POST ЗАПРОСОМ ОТПРАВИТЬ ТОКЕН,  CHAT-ID/USER_ID)

def start_api():
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

def start_bot():
    try:
        print("Запуск бота...")
        bot.polling(none_stop=True, interval=2)
    except Exception as e:
        print(f"Ошибка при запуске бота: {e}")
        time.sleep(2)
        start_bot()



if __name__ == "__main__":



    bot_thread = threading.Thread(target=start_bot)
    bot_thread.start()
    time.sleep(5)
    start_api()
