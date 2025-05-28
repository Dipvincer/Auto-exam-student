import os
import logging
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Configuration
    OPENAI_API_BASE = "https://openrouter.ai/api/v1"
    OPENAI_API_KEY = os.getenv("OPENROUTER_API_KEY")
    
    # Models
    MODELS = {
        "deepseek_v3": "deepseek/deepseek-chat-v3-0324",
        "deepseek_r1": "deepseek/deepseek-r1:free",
        "llama_3.1_nemotron": "nvidia/llama-3.1-nemotron-ultra-253b-v1:free",
        "qwen3_325b": "qwen/qwen3-235b-a22b:free",
        "gemini_2.5_flash": "google/gemini-2.5-flash-preview-05-20",
        "grok3_mini": "x-ai/grok-3-mini-beta",
        "gpt4o_mini": "openai/gpt-4o-mini",
    }
    
    # Defaults
    DEFAULT_MODEL = "deepseek_v3"
    DEFAULT_TEMPERATURE = 0.7
    DEFAULT_MAX_TOKENS = 2000    
    SYSTEM_LANGUAGE = "ru"

    # Evaluation params
    EVALUATION = {
        "exact_match_threshold": 0.9,
        "semantic_threshold": 0.75,
        "models": {
            "deepseek": "deepseek_v3",
            "minilm": "sentence-transformers/all-MiniLM-L6-v2"
        },
        "pass_border": {
            10: "Отлично",
            9: "Отлично",
            8: "Отлично",
            7: "Хорошо",
            6: "Хорошо",
            5: "Удовлетворительно",
            4: "Удовлетворительно",
            3: "Неудовлетворительно",
            2: "Неудовлетворительно",
            1: "Неудовлетворительно"
        }
    }

    # DB Configuration
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "exam_system")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

    # Auth Settings
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    
    # Registration Settings
    REGISTRATION_OPEN = os.getenv("REGISTRATION_OPEN", "True") == "True"

    # Logging configuration
    LOG_LEVEL = logging.INFO
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE = "loggs/exam_system.log"

    @staticmethod
    def setup_logging():
        """Configure logging for the application"""
        logging.basicConfig(
            level=Config.LOG_LEVEL,
            format=Config.LOG_FORMAT,
            handlers=[
                logging.FileHandler(Config.LOG_FILE),
                logging.StreamHandler()
            ]
        )