import os

from dotenv import load_dotenv

load_dotenv()

# Назначаем переменные из файла .env
BOT_TOKEN = os.getenv("BOT_TOKEN")
XUI_HOST = os.getenv("XUI_HOST")
XUI_USERNAME = os.getenv("XUI_USERNAME")
XUI_PASSWORD = os.getenv("XUI_PASSWORD")
PBK = os.getenv("PBK")
SID = os.getenv("SID")
