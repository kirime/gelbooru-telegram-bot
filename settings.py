import os

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
MODE = os.getenv('MODE', 'dev')
TOKEN = os.getenv('TOKEN')
CONNECT_TIMEOUT = 10
READ_TIMEOUT = 10

# Optional Gelbooru API credentials
API_KEY = os.getenv('GELBOORU_API_KEY', None)
USER_ID = os.getenv('GELBOORU_USER_ID', None)

# Optional webhook parameters
WEBHOOK_PATH = os.getenv('WEBHOOK_PATH')
PORT = int(os.getenv('WEBHOOK_PORT', '8443'))
