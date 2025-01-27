import os
import logging
import time
import threading
from flask import Flask, request
import requests

# 1) Определяем путь к текущей папке и к файлу лога
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGFILE_PATH = os.path.join(BASE_DIR, 'bot.log')

# 2) Настраиваем логгер
logging.basicConfig(
    filename=LOGFILE_PATH,
    level=logging.INFO,     # Можно заменить на logging.DEBUG, если нужно больше подробностей
    format='%(asctime)s [%(levelname)s] %(message)s'
)

app = Flask(__name__)

# --- Фоновая задача для периодического логирования ---
def periodic_logger():
    """Каждые 10 секунд записывает в лог 'Periodic log message: the bot is running'."""
    while True:
        logging.info("Periodic log message: the bot is running")
        time.sleep(10)

# Запускаем фоновый поток (демон), чтобы не блокировать Flask
thread = threading.Thread(target=periodic_logger, daemon=True)
thread.start()

@app.route('/talkme_webhook', methods=['POST'])
def talkme_webhook():
    # Пример обработки webhook от Talk-Me
    data = request.get_json(force=True)
    token = data.get("token", "")
    incoming_text = data.get("message", {}).get("text", "")

    logging.info(f"Получен webhook от Talk-Me: token={token}, text={incoming_text}")

    reply_text = f"Вы написали: {incoming_text}\nСпасибо за обращение!"
    url = "https://lcab.talk-me.ru/json/v1.0/customBot/send"
    body = {
        "content": {
            "type": "comment",
            "comment": reply_text
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
    """Маршрут проверки: при открытии браузером покажет, что бот с логированием запущен."""
    logging.info("GET / -> 'Bot with logging is running'")
    return "Bot with logging is running", 200

if __name__ == '__main__':
    # Локальный запуск. На хостинге uWSGI/Gunicorn самостоятельно запустит app
    app.run(port=5000, debug=True)


