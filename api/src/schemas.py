"""
Pydantic схемы для Space Marine игры
"""
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class CharacterType(str, Enum):
    """Типы персонажей"""
    SPACE_MARINE = "space_marine"
    ORK = "ork"
    CHAOS_CULTIST = "chaos_cultist"
    TYRANID = "tyranid"
    NECRON = "necron"
    ELDAR = "eldar"
    TAU = "tau"


class Character(BaseModel):
    """Базовый класс персонажа"""
    name: str
    character_type: CharacterType
    health: int = Field(ge=0, description="Здоровье персонажа")
    max_health: int = Field(ge=1, description="Максимальное здоровье")
    attack_power: int = Field(ge=1, description="Сила атаки")
    
    class Config:
        use_enum_values = True


class Enemy(Character):
    """Враг"""
    pass


class SpaceMarine(Character):
    """Space Marine"""
    character_type: CharacterType = CharacterType.SPACE_MARINE


class CombatResult(BaseModel):
    """Результат боя"""
    attacker: Character
    defender: Character
    dice_roll: int = Field(ge=1, le=6, description="Результат броска кубика")
    damage: int = Field(ge=0, description="Нанесенный урон")
    defender_health_after: int = Field(ge=0, description="Здоровье защитника после атаки")
    is_defender_defeated: bool = Field(description="Побежден ли защитник")


class GameState(BaseModel):
    """Состояние игры"""
    space_marine: SpaceMarine
    enemies: List[Enemy] = Field(description="Список врагов")
    current_enemy_index: int = Field(ge=0, description="Индекс текущего врага")
    round_number: int = Field(ge=1, description="Номер раунда")
    is_game_over: bool = Field(default=False, description="Игра окончена")
    is_victory: bool = Field(default=False, description="Победа Space Marine")
    
    @property
    def current_enemy(self) -> Optional[Enemy]:
        """Текущий враг"""
        if 0 <= self.current_enemy_index < len(self.enemies):
            return self.enemies[self.current_enemy_index]
        return None
