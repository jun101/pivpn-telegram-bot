import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BOT_ADMIN_ID = int(os.getenv("BOT_ADMIN_ID"))
CONFIG_DIR = os.getenv("CONFIG_DIR", "./mock_configs")
MOCK_MODE = os.getenv("MOCK_MODE", "false").lower() == "true"
