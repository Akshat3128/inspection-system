import logging
from datetime import datetime

def log_request(route):
    logging.info(f"[{datetime.now()}] Request made to {route}")
