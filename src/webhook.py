import os
import logging
import time
import threading
from flask import Flask, request
import requests
import openai

# ------------------------------------------------------
# 1) Настройка прокси (если вам действительно нужно 
#    отправлять запросы к OpenAI через прокси)
# ------------------------------------------------------
proxy_host = "213.225.237.177"
proxy_port = "9239"
proxy_user = "user27099"
proxy_pass = "qf08ja"

proxy_url = f"http://{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}"
os.environ['http_proxy'] = proxy_url
os.environ['https_proxy'] = proxy_url

# ------------------------------------------------------
# 2) Настройка OpenAI API
# ------------------------------------------------------
openai.api_key = "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"  # <-- вставьте сюда реальный API-ключ

# ------------------------------------------------------
# 3) Логирование в файл
# ------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGFILE_PATH = os.path.join(BASE_DIR, 'bot.log')

logging.basicConfig(
    filename=LOGFILE_PATH,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

# ------------------------------------------------------
# Flask-приложение
# ------------------------------------------------------
app = Flask(__name__)

# Фоновая задача: каждые 10 секунд записывать в лог,
# чтобы было видно, что бот "жив"
def periodic_logger():
    while True:
        logging.info("Periodic log message: the bot is running")
        time.sleep(10)

thread = threading.Thread(target=periodic_logger, daemon=True)
thread.start()

# ------------------------------------------------------
# Функция для вызова ChatGPT
# ------------------------------------------------------
def get_chatgpt_response(user_text):
    """
    Отправляем текст пользователя в ChatGPT (модель gpt-3.5-turbo).
    Можно настроить "роль" и "поведение" бота через "system"-сообщение.
    """
    try:
        # Здесь задаём системное сообщение (роль), можно изменить
        system_role = (
            "Ты — дружелюбный ассистент, который отвечает чётко, кратко и по делу. "
            "Если пользователь задаёт вопрос, дай полезный ответ. "
            "По возможности используй вежливую, дружелюбную лексику."
        )

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_role},
                {"role": "user", "content": user_text}
            ],
            temperature=0.7,  # Степень "творчества" (0.0 - максимально детерминирован, 1.0 - более разнообразен)
        )
        # Достаём ответ из структуры
        answer = response["choices"][0]["message"]["content"]
        return answer

    except Exception as e:
        logging.error(f"Ошибка при запросе к ChatGPT: {e}")
        # Можно вернуть какую-то фразу по умолчанию
        return "Извините, произошла ошибка при запросе к ИИ."

# ------------------------------------------------------
# Маршрут для приёма вебхуков от Talk-Me
# ------------------------------------------------------
@app.route('/talkme_webhook', methods=['POST'])
def talkme_webhook():
    data = request.get_json(force=True)
    token = data.get("token", "")
    incoming_text = data.get("message", {}).get("text", "")

    logging.info(f"Получен webhook от Talk-Me: token={token}, text={incoming_text}")

    # Вместо простого ответа, спрашиваем ChatGPT
    reply_text = get_chatgpt_response(incoming_text)

    # Формируем запрос обратно в Talk-Me
    url = "https://lcab.talk-me.ru/json/v1.0/customBot/send"
    body = {
        "content": {
            "text": reply_text  # в их документации пример: {"content": {"text": "string"}}
        }
    }
    headers = {
        "X-Token": token,
        "Content-Type": "application/json"
    }

    # Отправляем ответ в Talk-Me
    response = requests.post(url, json=body, headers=headers)
    logging.info(f"Отправили ответ в Talk-Me: {response.status_code} {response.text}")

    # Возвращаем OK, чтобы Talk-Me знал, что вебхук обработан
    return "OK", 200

# ------------------------------------------------------
# Маршрут проверки
# ------------------------------------------------------
@app.route('/', methods=['GET'])
def index():
    logging.info("GET / -> Bot with ChatGPT is running")
    return "Bot with ChatGPT is running", 200

# ------------------------------------------------------
# Локальный запуск (не используется на боевом хостинге,
# там uWSGI/Gunicorn сами вызывают app)
# ------------------------------------------------------
if __name__ == '__main__':
    app.run(port=5000, debug=True)






