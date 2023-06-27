import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
FORMAT = '%(asctime)s, %(levelname)s, %(name)s, %(message)s'