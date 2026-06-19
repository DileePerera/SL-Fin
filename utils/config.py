import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "llama3.1:8b")
    STRONG_MODEL = os.getenv("STRONG_MODEL", "llama3.1:8b")
    FAST_MODEL = os.getenv("FAST_MODEL", "llama3.1:8b")
    
    VECTOR_DB_PATH = "vectorstore/finance_db"
    DATA_FOLDER = "data/user_data"
    
    # Sri Lanka specific
    DEFAULT_CURRENCY = "LKR"
    SUPPORTED_CURRENCIES = ["LKR", "USD", "INR", "EUR"]