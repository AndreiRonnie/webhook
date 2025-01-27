import os
import logging
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

@app.route('/talkme_webhook', methods=['POST'])
def talkme_webhook():
    # 1) Получаем JSON из тела запроса
    data = request.get_json(force=True)

    # 2) Извлекаем нужные поля
    token = data.get("token", "")
    incoming_text = data.get("message", {}).get("text", "")

    # Запишем информацию в лог
    logging.info(f"Получен webhook от Talk-Me: token={token}, text={incoming_text}")

    # 3) Формируем ответ (здесь может быть вызов вашего ИИ)
    reply_text = f"Вы написали: {incoming_text}\nСпасибо за обращение!"

    # 4) Готовим POST-запрос на Talk-Me
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

    # Отправляем
    response = requests.post(url, json=body, headers=headers)
    logging.info(f"Отправили ответ в Talk-Me: {response.status_code} {response.text}")

    # 5) Возвращаем "OK", чтобы Talk-Me знал, что webhook успешно обработан
    return "OK", 200

@app.route('/', methods=['GET'])
def index():
    # Для проверки доступности сервера
    logging.info("GET /  -> Server is running")
    return "Server is running", 200


if __name__ == '__main__':
    # Локальный запуск (при деплое на хостинге uWSGI/Gunicorn сам вызовет app)
    app.run(port=5000, debug=True)

