import logging
from pythonjsonlogger import jsonlogger
import os
import datetime
import pytz


utc_plus_3 = pytz.timezone('Europe/Moscow')
# Create logs directory if it doesn't exist
log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)

# Log file path
cur_time = datetime.datetime.now()
log_file_path = os.path.join(
    log_dir,
    f'application_{cur_time.strftime("%Y-%m-%d_%H-%M-%S")}.jsonl')


# Configure logging
logger = logging.getLogger('MyLogger')
logger.setLevel(logging.DEBUG)

# Create a file handler
file_handler = logging.FileHandler(log_file_path)

# Create a JSON formatter
formatter = jsonlogger.JsonFormatter()
file_handler.setFormatter(formatter)

# Add the file handler to the logger
logger.addHandler(file_handler)

# Example log messages
logger.info("Logger started")


def cur_datetime_string():
    cur_time = datetime.datetime.now(utc_plus_3)
    return cur_time.strftime("%Y-%m-%d_%H-%M-%S")


def log_action(message, action: str):
    cur_time = cur_datetime_string()
    logger.info(f"Time: {cur_time}; chat: {message.chat.id}; action: {action}")


def log_http_request(query: str, response: str):
    cur_time = cur_datetime_string()
    logger.info(f"Time: {cur_time}; query: {query}; response: {response}")
