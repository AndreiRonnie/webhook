import os
import logging
import time
import threading
import sys
from flask import Flask, request
import requests
import openai

# Дополнительная библиотека для проверки версии openai
import pkg_resources


# ------------------------------------------------------
# 0) Проверим версию openai и выведем в лог
# ------------------------------------------------------
try:
    openai_version = pkg_resources.get_distribution("openai").version
except pkg_resources.DistributionNotFound:
    openai_version = "Not installed"

print(f"[DEBUG] Python version: {sys.version}")
print(f"[DEBUG] Installed openai version: {openai_version}")


# ------------------------------------------------------
# 1) Настройка прокси (если нужно)
# ------------------------------------------------------
proxy_host = "213.225.237.177"
proxy_port = "9239"
proxy_user = "user27099"
proxy_pass = "qf08ja"

proxy_url = f"http://{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}"
#os.environ['http_proxy'] = proxy_url
#os.environ['https_proxy'] = proxy_url

# ------------------------------------------------------
# 2) Настройка OpenAI API (старый синтаксис ChatCompletion)
# ------------------------------------------------------
openai.api_key = "sk-..."  # <-- вставьте сюда реальный API-ключ

# ------------------------------------------------------
# 3) Логирование в файл
# ------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGFILE_PATH = os.path.join(BASE_DIR, 'bot.log')

# Можно выставить level=logging.DEBUG, чтобы логировать больше деталей
logging.basicConfig(
    filename=LOGFILE_PATH,
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

logging.info(f"==== Bot startup ====")
logging.info(f"Running on Python {sys.version}")
logging.info(f"OpenAI library version: {openai_version}")


# ------------------------------------------------------
# Flask-приложение
# ------------------------------------------------------
app = Flask(__name__)

# Фоновая задача: каждые 10 секунд записывать в лог
def periodic_logger():
    while True:
        logging.info("Periodic log message: the bot is running")
        time.sleep(10)

thread = threading.Thread(target=periodic_logger, daemon=True)
thread.start()


# ------------------------------------------------------
# Функция для вызова ChatGPT (ChatCompletion)
# ------------------------------------------------------
def get_chatgpt_response(user_text):
    """
    Отправляем текст пользователя в ChatGPT (модель gpt-3.5-turbo).
    Можно настроить "роль" и "поведение" бота через "system"-сообщение.
    """
    logging.debug("get_chatgpt_response() called with user_text=%r", user_text)

    try:
        system_role = (
            "Ты — дружелюбный ассистент, который отвечает чётко, кратко и по делу. "
            "Если пользователь задаёт вопрос, дай полезный ответ. "
            "По возможности используй вежливую, дружелюбную лексику."
        )

        logging.debug("About to call openai.ChatCompletion.create...")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_role},
                {"role": "user", "content": user_text}
            ],
            temperature=0.7,  
            request_timeout=30  # Устанавливаем таймаут в 30 секунд
        )
        logging.debug("Response received from OpenAI")

        # Достаём ответ из структуры
        answer = response["choices"][0]["message"]["content"]
        logging.debug("Parsed answer from response: %r", answer)

        return answer

    except Exception as e:
        logging.error(f"Ошибка при запросе к ChatGPT: {e}")
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

    logging.debug("Calling get_chatgpt_response with incoming_text=%r", incoming_text)
    reply_text = get_chatgpt_response(incoming_text)
    logging.debug(f"Got reply_text={reply_text}")

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

    logging.debug("Sending reply to Talk-Me: url=%s, body=%s", url, body)
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
# Локальный запуск
# ------------------------------------------------------
if __name__ == '__main__':
    app.run(port=5000, debug=True)





