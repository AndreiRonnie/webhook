import os
import logging
import time
import threading
from flask import Flask, request
import requests

# Определяем путь к текущей папке и к файлу лога
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGFILE_PATH = os.path.join(BASE_DIR, 'bot.log')

# Настраиваем логгер
logging.basicConfig(
    filename=LOGFILE_PATH,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

app = Flask(__name__)

# Пример фонового потока, который пишет в лог каждые 10 секунд (для наглядности)
def periodic_logger():
    while True:
        logging.info("Periodic log message: the bot is running")
        time.sleep(10)

thread = threading.Thread(target=periodic_logger, daemon=True)
thread.start()

@app.route('/talkme_webhook', methods=['POST'])
def talkme_webhook():
    data = request.get_json(force=True)
    token = data.get("token", "")
    incoming_text = data.get("message", {}).get("text", "")

    logging.info(f"Получен webhook от Talk-Me: token={token}, text={incoming_text}")

    # Логика ответа
    if incoming_text.lower() == "/start":
        reply_text = "Добро пожаловать! Чем могу помочь?"
    else:
        reply_text = f"Вы написали: {incoming_text}\nСпасибо за обращение!"

    # Ссылаемся на /customBot/send
    url = "https://lcab.talk-me.ru/json/v1.0/customBot/send"

    # --- Главное отличие: "content": {"text": "..."} ---
    body = {
        "content": {
            "text": reply_text
        }
    }

    headers = {
        "X-Token": token,
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=body, headers=headers)
    logging.info(f"Отправили ответ в Talk-Me: {response.status_code} {response.text}")

    return "OK", 200

@app.route('/', methods=['GET'])
def index():
    logging.info("GET / -> Bot with text-based content is running")
    return "Bot with text-based content is running", 200

if __name__ == '__main__':
    app.run(port=5000, debug=True)




