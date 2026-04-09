import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path('.') / '.env', override=False)

NAVER_CLIENT_ID = os.getenv('NAVER_CLIENT_ID', '').strip()
NAVER_CLIENT_SECRET = os.getenv('NAVER_CLIENT_SECRET', '').strip()
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '').strip()
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '').strip()
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///local.db').strip()
