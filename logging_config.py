"""Module for configuring logging system for the Military Image Analysis System."""
import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime
from typing import Optional

def configure_logging(log_file: Optional[str] = None, log_level: str = "INFO") -> logging.Logger:
    """Configure the logging system with file and console output.

    Args:
        log_file: Path to the log file. Defaults to 'logs/military_system_{date}.log'.
        log_level: Logging level (e.g., 'DEBUG', 'INFO', 'ERROR'). Defaults to 'INFO'.

    Returns:
        Configured logger instance.
    """
    # إنشاء اسم ملف السجل إذا لم يُحدد
    if log_file is None:
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        date_str = datetime.now().strftime("%Y%m%d")
        log_file = os.path.join(log_dir, f"military_system_{date_str}.log")

    # إعداد المُسجّل
    logger = logging.getLogger("MilitarySystem")
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # منع التكرار إذا كان المُسجّل مُهيأ بالفعل
    if logger.handlers:
        logger.handlers.clear()

    # تنسيق السجل: الوقت، المستوى، الملف/السطر، والرسالة
    log_format = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # معالج ملف السجل مع التدوير (حجم أقصى 5 ميغابايت، 3 نسخ احتياطية)
    try:
        file_handler = RotatingFileHandler(
            log_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
        )
        file_handler.setFormatter(log_format)
        file_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        logger.addHandler(file_handler)
    except Exception as e:
        # تسجيل فشل إعداد ملف السجل إلى وحدة التحكم كإجراء احتياطي
        console_fallback = logging.StreamHandler()
        console_fallback.setFormatter(log_format)
        logger.addHandler(console_fallback)
        logger.error(f"Failed to configure file logging: {e}")

    # معالج وحدة التحكم لعرض السجلات في الطرفية
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_format)
    console_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    logger.addHandler(console_handler)

    # تسجيل بدء إعداد النظام
    logger.info("Logging system configured successfully")
    return logger