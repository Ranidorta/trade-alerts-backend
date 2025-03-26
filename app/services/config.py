import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BYBIT_API_KEY = os.getenv("BYBIT_API_KEY", "")
    BYBIT_API_SECRET = os.getenv("BYBIT_API_SECRET", "")
    MAX_WORKERS = int(os.getenv("MAX_WORKERS", 5))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
