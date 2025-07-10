"""
Конфигурация логирования
"""
import sys
from loguru import logger
from .config import settings


def get_logger(name: str = "APP"):
    """
    Получить настроенный логгер
    
    Args:
        name: Имя логгера
    
    Returns:
        logger: Настроенный логгер
    """
    
    # Удаляем стандартный логгер
    logger.remove()
    
    # Добавляем консольный вывод с цветами
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.log_level,
        colorize=True
    )
    
    # Добавляем запись в файл
    logger.add(
        "logs/app.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=settings.log_level,
        rotation="10 MB",
        retention="7 days",
        compression="zip"
    )
    
    # Привязываем имя
    return logger.bind(name=name) 