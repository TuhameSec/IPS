"""Module for centralized configuration settings."""
import os
from dotenv import load_dotenv
from logging_config import configure_logging
from typing import Optional

logger = configure_logging()

class Config:
    """Class to manage system configuration settings."""
    
    def __init__(self):
        """Initialize configuration by loading environment variables."""
        load_dotenv()
        self._load_settings()
        logger.info("Configuration initialized successfully")

    def _load_settings(self):
        """Load and validate configuration settings from environment variables."""
        # إعدادات قاعدة البيانات
        self.DB_HOST = os.getenv("DB_HOST", "localhost")
        self.DB_NAME = os.getenv("DB_NAME", "MilitaryDB")
        self.DB_USER = os.getenv("DB_USER")
        self.DB_PASSWORD = os.getenv("DB_PASSWORD")
        self.SSL_ROOT_CERT_PATH = os.getenv("SSL_ROOT_CERT_PATH")

        # إعدادات التشفير
        self.ENCRYPTION_PASSWORD = os.getenv("ENCRYPTION_PASSWORD")
        self.ENCRYPTION_SALT = os.getenv("ENCRYPTION_SALT")

        # إعدادات السجل
        self.LOG_FILE = os.getenv("LOG_FILE")
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

        # إعدادات الكاميرا
        self.FRAME_WIDTH = int(os.getenv("FRAME_WIDTH", 640))
        self.FRAME_HEIGHT = int(os.getenv("FRAME_HEIGHT", 480))
        self.MAX_FRAME_QUEUE = int(os.getenv("MAX_FRAME_QUEUE", 5))

        # إعدادات التنبيهات
        self.ALERT_THRESHOLD = os.getenv("ALERT_THRESHOLD", "high").lower()

        # التحقق من الإعدادات الحساسة
        self._validate_settings()

    def _validate_settings(self):
        """Validate critical configuration settings."""
        critical_settings = [
            ("DB_USER", self.DB_USER),
            ("DB_PASSWORD", self.DB_PASSWORD),
            ("ENCRYPTION_PASSWORD", self.ENCRYPTION_PASSWORD),
        ]
        for name, value in critical_settings:
            if not value:
                logger.error(f"Missing critical setting: {name}")
                raise ValueError(f"Configuration error: {name} is required")

    def get_setting(self, key: str, default: Optional[any] = None) -> any:
        """Get a configuration setting by key.

        Args:
            key: Name of the setting.
            default: Default value if key is not found.

        Returns:
            Value of the setting or default.
        """
        return getattr(self, key, default)

config = Config()