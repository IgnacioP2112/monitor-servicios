#Hace la consulta al sitio Web
#
#
import requests
import time
from config import TIMEOUT

def check_service(url):
    start_time = time.time()

    try:
        response = requests.get(url, timeout=TIMEOUT)
        response_time = time.time() - start_time

        return {
            "url": url,
            "status": response.status_code,
            "response_time": round(response_time, 3),
            "error": None
        }

    except requests.exceptions.RequestException as e:
        return {
            "url": url,
            "status": None,
            "response_time": None,
            "error": str(e)
        }