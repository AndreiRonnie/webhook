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
# 2) Настройка OpenAI API (новый синтаксис: openai.Chat)
# ------------------------------------------------------
openai.api_key = "sk-sJkin25L76lyn34kLtuh0gp6KLGVh64JmEXhfZI_XjT3BlbkFJ71ug9rtGDrotO3iNxFdvXeI5jb8OzX3yE1jnfSnEgA"

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
# Функция для вызова ChatGPT (с новым методом openai.Chat)
# ------------------------------------------------------
def get_chatgpt_response(user_text):
    """
    Отправляем текст пользователя в ChatGPT (модель gpt-3.5-turbo).
    Можно настроить "роль" и "поведение" бота через "system"-сообщение.
    """
    try:
        system_role = (
            "Ты — дружелюбный ассистент, который отвечает чётко, кратко и по делу. "
            "Если пользователь задаёт вопрос, дай полезный ответ. "
            "По возможности используй вежливую, дружелюбную лексику."
        )

        # Используем новый синтаксис openai.Chat.create
        response = openai.Chat.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_role},
                {"role": "user", "content": user_text}
            ],
            temperature=0.7,  # Степень "творчества"
        )
        # Достаём ответ
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
            "text": reply_text
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

