import os
import requests
import logging

# Настраиваем логирование
logging.basicConfig(
    filename='bot.log',          # Имя лог-файла
    level=logging.INFO,          # Уровень логирования
    format='%(asctime)s - %(levelname)s - %(message)s'  # Формат записей
)
logger = logging.getLogger(__name__)

proxy_user = "user27099"
proxy_pass = "qf08ja"
proxy_host = "213.225.237.177"
proxy_port = "9239"

proxy_url = f"http://{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}"

proxies = {
    "http": proxy_url,
    "https": proxy_url
}

try:
    logger.info("Отправляем GET-запрос к https://api.openai.com/v1/models через прокси...")
    r = requests.get("https://api.openai.com/v1/models", proxies=proxies, timeout=15)
    logger.info(f"Status code: {r.status_code}")
    logger.info(f"Response text: {r.text}")
except Exception as e:
    logger.error(f"Ошибка при запросе: {e}")






