import telebot
from fastapi import (FastAPI, Depends, HTTPException, Request)
from fastapi.middleware.cors import (CORSMiddleware)
from fastapi.staticfiles import (StaticFiles)

from app.logging_config import log

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.on_event("startup")
async def startup():
    log.bind(type="app").info("Application start up")


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


bot.polling(none_stop=True, interval=0)


@app.post("/send_message")
async def send_message(request: Request):
    data = await request.json()
    bot.send_message(data["telegram_id"], data["massage"])
    return True


def main():
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=80, reload=True)


if __name__ == "__main__":
    main()
