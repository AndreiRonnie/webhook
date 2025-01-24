from flask import Flask, request
import requests

app = Flask(__name__)

# Укажите здесь свой реальный токен бота:
BOT_TOKEN = "8175659323:AAFxJXsTFe0pRAqEUfNlixYMhXkuxOs8wgY"


@app.route('/', methods=['GET'])
def index():
    """
    Тестовый маршрут: при обращении GET-запросом вернёт простой текст.
    """
    return "Hello! This is the root page. Bot is running.", 200


@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    """
    Эндпоинт для приёма вебхука от Telegram.
    """
    # 1) Считываем JSON, пришедший в POST-запросе
    update = request.get_json(force=True)

    # 2) Обработка входящего сообщения
    if "message" in update and "text" in update["message"]:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"]["text"]

        if text.lower() == "привет":
            reply_text = "Здравствуйте! Чем могу помочь?"
            send_message(chat_id, reply_text)

        elif text == "/start":
            reply_text = (
                "Привет! Я бот. Чем могу помочь?\n\n"
                "Попробуй написать 'Привет' или /start, чтобы проверить работу."
            )
            send_message(chat_id, reply_text)

    # 3) Возвращаем "OK", чтобы Telegram понял, что запрос обработан
    return "OK", 200


def send_message(chat_id, text):
    """
    Функция, отправляющая сообщение пользователю через Telegram Bot API.
    """
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    resp = requests.post(url, json=payload)
    return resp.json()


if __name__ == '__main__':
    """
    Локальный запуск:
    Запустится Flask-сервер на 0.0.0.0:5000 (http://127.0.0.1:5000/).
    При деплое на Majordomo уWSGI сам будет использовать app=Flask(__name__).
    """
    app.run(host='0.0.0.0', port=5000, debug=True)
