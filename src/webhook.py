import os
import requests
import logging
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Отключаем предупреждения о SSL (только для тестирования)
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Определяем путь к текущей папке и к файлу лога
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGFILE_PATH = os.path.join(BASE_DIR, 'bot.log')

# Настраиваем логгер
logging.basicConfig(
    filename=LOGFILE_PATH,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

def periodic_logger():
    while True:
        logging.info("Periodic log message: the bot is running")
        time.sleep(10)

thread = threading.Thread(target=periodic_logger, daemon=True)
thread.start()

proxy_user = "user27099"
proxy_pass = "qf08ja"
proxy_host = "213.225.237.177"
proxy_port = "9239"
proxy_url = f"http://{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}"
proxies = {
"http": proxy_url,
"https": proxy_url
}

# Ваш токен аутентификации
auth_token = "your_auth_token_here"

try:
logger.info("Отправляем GET-запрос к https://api.openai.com/v1/models через прокси...")
logger.debug(f"Прокси URL: {proxy_url}")

headers = {
'Authorization': f'Bearer {auth_token}'
}

r = requests.get("https://api.openai.com/v1/models", proxies=proxies, verify=False, timeout=30, headers=headers)
logger.info(f"Status code: {r.status_code}")
logger.info(f"Response text: {r.text}")
except Exception as e:
logger.error(f"Ошибка при запросе: {e}")
logger.debug(f"Дополнительная информация об ошибке: {str(e)}")

# Попробуем использовать другой прокси-сервер (если есть)
alternative_proxy_host = "новый_прокси_хост" # Замените на реальный хост
alternative_proxy_port = "новый_прокси_порт" # Замените на реальный порт
alternative_proxy_url = f"http://{proxy_user}:{proxy_pass}@{alternative_proxy_host}:{alternative_proxy_port}"
alternative_proxies = {
"http": alternative_proxy_url,
"https": alternative_proxy_url
}

try:
logger.info("Отправляем GET-запрос к https://api.openai.com/v1/models через альтернативный прокси...")
logger.debug(f"Альтернативный прокси URL: {alternative_proxy_url}")

headers = {
'Authorization': f'Bearer {auth_token}'
}

r = requests.get("https://api.openai.com/v1/models", proxies=alternative_proxies, verify=False, timeout=30, headers=headers)
logger.info(f"Status code: {r.status_code}")
logger.info(f"Response text: {r.text}")
except Exception as e:
logger.error(f"Ошибка при запросе через альтернативный прокси: {e}")
logger.debug(f"Дополнительная информация об ошибке: {str(e)}")







