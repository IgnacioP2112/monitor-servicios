
#Configuración de los sitios que se van a monitorear.

import os
from dotenv import load_dotenv
load_dotenv()

URLS = os.getenv("URLS", "https://google.com").split(",")

CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 30))
TIMEOUT        = int(os.getenv("TIMEOUT", 10))
MAX_FAILURES   = int(os.getenv("MAX_FAILURES", 3))
