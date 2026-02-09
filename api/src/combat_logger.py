"""
Логирование боевых действий
"""
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any


def setup_combat_logger():
    """Настройка логгера для боевых действий"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / f"combat_{datetime.now().strftime('%Y%m%d')}.log"
    
    logger = logging.getLogger("combat")
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
    
    return logger


def log_combat_result(logger: logging.Logger, combat_result: Any, round_number: int = None):
    """
    Логирует результат боя (упрощенная версия без схем)
    """
    # Функция оставлена для совместимости, но логирование теперь в main.py
    pass


def log_shout(logger: logging.Logger, character_name: str, character_type: str, shout: str):
    """
    Логирует крик персонажа
    
    Args:
        logger: Логгер
        character_name: Имя персонажа
        character_type: Тип персонажа
        shout: Текст крика
    """
    logger.info(f"{character_name} ({character_type}) кричит: \"{shout}\"")


def log_game_start(logger: logging.Logger, space_marine_name: str, num_enemies: int):
    """
    Логирует начало игры
    
    Args:
        logger: Логгер
        space_marine_name: Имя Space Marine
        num_enemies: Количество врагов
    """
    logger.info("=" * 60)
    logger.info(f"НАЧАЛО ИГРЫ - Space Marine: {space_marine_name}, Врагов: {num_enemies}")
    logger.info("=" * 60)


def log_game_end(logger: logging.Logger, is_victory: bool, final_round: int = None):
    """
    Логирует окончание игры
    
    Args:
        logger: Логгер
        is_victory: Победа или поражение
        final_round: Финальный раунд
    """
    result = "ПОБЕДА!" if is_victory else "ПОРАЖЕНИЕ!"
    round_info = f" (Раунд {final_round})" if final_round else ""
    logger.info("=" * 60)
    logger.info(f"КОНЕЦ ИГРЫ - {result}{round_info}")
    logger.info("=" * 60)
