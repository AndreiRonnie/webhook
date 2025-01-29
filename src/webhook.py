import os
import logging
import time
import threading
from flask import Flask, request
import requests
import openai

# NEW: Подключаем dotenv
from dotenv import load_dotenv

# ------------------------------------------------------
# 1) Загрузка переменных окружения из .env
# ------------------------------------------------------
load_dotenv()  # Эта функция автоматически найдёт и загрузит .env, если он лежит рядом.
openai.api_key = os.getenv("OPENAI_API_KEY", "")

# ------------------------------------------------------
# 2) Настройка прокси (если нужно)
# ------------------------------------------------------
proxy_host = "213.225.237.177"
proxy_port = "9239"
proxy_user = "user27099"
proxy_pass = "qf08ja"

proxy_url = f"http://{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}"
os.environ['http_proxy'] = proxy_url
os.environ['https_proxy'] = proxy_url

# ------------------------------------------------------
# 3) Логирование
# ------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGFILE_PATH = os.path.join(BASE_DIR, 'bot.log')

logging.basicConfig(
    filename=LOGFILE_PATH,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

app = Flask(__name__)

def periodic_logger():
    while True:
        logging.info("Periodic log message: the bot is running")
        time.sleep(10)

thread = threading.Thread(target=periodic_logger, daemon=True)
thread.start()

def get_chatgpt_response(user_text):
    try:
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
            temperature=0.7,
        )
        answer = response["choices"][0]["message"]["content"]
        return answer
    except Exception as e:
        logging.error(f"Ошибка при запросе к ChatGPT: {e}")
        return "Извините, произошла ошибка при запросе к ИИ."

@app.route('/talkme_webhook', methods=['POST'])
def talkme_webhook():
    data = request.get_json(force=True)
    token = data.get("token", "")
    incoming_text = data.get("message", {}).get("text", "")

    logging.info(f"Получен webhook от Talk-Me: token={token}, text={incoming_text}")

    reply_text = get_chatgpt_response(incoming_text)

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

    response = requests.post(url, json=body, headers=headers)
    logging.info(f"Отправили ответ в Talk-Me: {response.status_code} {response.text}")

    return "OK", 200

@app.route('/', methods=['GET'])
def index():
    logging.info("GET / -> Bot with ChatGPT is running")
    return "Bot with ChatGPT is running", 200

if __name__ == '__main__':
    app.run(port=5000, debug=True)





