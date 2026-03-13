
from datetime import datetime
import os


LOG_FILE = "logs/monitor.log"

def log_result(result):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if result["error"]:
        message = f"{timestamp} | ERROR | {result['url']} | {result['error']}"
    else:
        message = f"{timestamp} | OK | {result['url']} | {result['status']} | {result['response_time']}s"


    print(message)

    with open(LOG_FILE, "a") as file:
        file.write(message +"\n")