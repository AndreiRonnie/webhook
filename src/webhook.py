import os
import requests
import logging
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# -------------------------
# Отключаем предупреждения о SSL (только для тестирования!)
# -------------------------
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# -------------------------
# Настраиваем логирование
# -------------------------
logging.basicConfig(
    filename='bot.log',          # Лог пишем в bot.log
    level=logging.DEBUG,         # Уровень DEBUG, чтобы видеть максимум инфы
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# -------------------------
# Параметры прокси
# -------------------------
proxy_user = "user27099"
proxy_pass = "qf08ja"
proxy_host = "213.225.237.177"
proxy_port = "9239"

proxy_url = f"http://{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}"

proxies_primary = {
    "http": proxy_url,
    "https": proxy_url
}

# -------------------------
# Токен OpenAI (подставьте реальный, напр. sk-...)
# -------------------------
auth_token = "sk-REPLACE_WITH_REAL_TOKEN"

# -------------------------
# Запрос к OpenAI через первичный прокси
# -------------------------
try:
    logger.info("Отправляем GET-запрос к https://api.openai.com/v1/models через ПЕРВИЧНЫЙ прокси...")
    logger.debug(f"Прокси URL: {proxy_url}")

    headers = {
        'Authorization': f'Bearer {auth_token}'
    }

    r = requests.get(
        "https://api.openai.com/v1/models",
        proxies=proxies_primary,
        verify=False,      # Отключаем проверку SSL-сертификата
        timeout=30,
        headers=headers
    )
    logger.info(f"[PRIMARY] Status code: {r.status_code}")
    logger.info(f"[PRIMARY] Response text: {r.text}")

except Exception as e:
    logger.error(f"[PRIMARY] Ошибка при запросе: {e}")
    logger.debug(f"[PRIMARY] Доп. инфо об ошибке: {str(e)}")


# -------------------------
# Параметры альтернативного прокси (заглушка, замените на реальные)
# -------------------------
alternative_proxy_host = "NEW_PROXY_HOST"  # Замените на реальный хост
alternative_proxy_port = "NEW_PROXY_PORT"  # Замените на реальный порт
alternative_proxy_url = f"http://{proxy_user}:{proxy_pass}@{alternative_proxy_host}:{alternative_proxy_port}"

proxies_alternative = {
    "http": alternative_proxy_url,
    "https": alternative_proxy_url
}

# -------------------------
# Запрос к OpenAI через АЛЬТЕРНАТИВНЫЙ прокси
# -------------------------
try:
    logger.info("Отправляем GET-запрос к https://api.openai.com/v1/models через АЛЬТЕРНАТИВНЫЙ прокси...")
    logger.debug(f"Альтернативный прокси URL: {alternative_proxy_url}")

    headers = {
        'Authorization': f'Bearer {auth_token}'
    }

    r = requests.get(
        "https://api.openai.com/v1/models",
        proxies=proxies_alternative,
        verify=False,
        timeout=30,
        headers=headers
    )
    logger.info(f"[ALTERNATIVE] Status code: {r.status_code}")
    logger.info(f"[ALTERNATIVE] Response text: {r.text}")

except Exception as e:
    logger.error(f"[ALTERNATIVE] Ошибка при запросе через альтернативный прокси: {e}")
    logger.debug(f"[ALTERNATIVE] Доп. инфо об ошибке: {str(e)}")







