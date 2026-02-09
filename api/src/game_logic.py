"""
Логика игры Space Marine
"""
import random
from typing import List, Optional

from src.schemas import (
    CharacterType, Character, Enemy, SpaceMarine, 
    GameState, CombatResult
)


def roll_dice(sides: int = 6) -> int:
    """Бросок кубика"""
    return random.randint(1, sides)


class EnemyFactory:
    """Фабрика для создания врагов"""
    
    @staticmethod
    def create_ork(name: str = "Ork Boy") -> Enemy:
        return Enemy(
            name=name,
            character_type=CharacterType.ORK,
            health=30,
            max_health=30,
            attack_power=4
        )
    
    @staticmethod
    def create_chaos_cultist(name: str = "Chaos Cultist") -> Enemy:
        return Enemy(
            name=name,
            character_type=CharacterType.CHAOS_CULTIST,
            health=20,
            max_health=20,
            attack_power=3
        )
    
    @staticmethod
    def create_tyranid(name: str = "Tyranid Warrior") -> Enemy:
        return Enemy(
            name=name,
            character_type=CharacterType.TYRANID,
            health=35,
            max_health=35,
            attack_power=5
        )
    
    @staticmethod
    def create_necron(name: str = "Necron Warrior") -> Enemy:
        return Enemy(
            name=name,
            character_type=CharacterType.NECRON,
            health=25,
            max_health=25,
            attack_power=4
        )
    
    @staticmethod
    def create_eldar(name: str = "Eldar Guardian") -> Enemy:
        return Enemy(
            name=name,
            character_type=CharacterType.ELDAR,
            health=22,
            max_health=22,
            attack_power=5
        )
    
    @staticmethod
    def create_tau(name: str = "Tau Fire Warrior") -> Enemy:
        return Enemy(
            name=name,
            character_type=CharacterType.TAU,
            health=24,
            max_health=24,
            attack_power=4
        )
    
    @staticmethod
    def create_random_enemy() -> Enemy:
        """Создает случайного врага"""
        enemy_types = [
            EnemyFactory.create_ork,
            EnemyFactory.create_chaos_cultist,
            EnemyFactory.create_tyranid,
            EnemyFactory.create_necron,
            EnemyFactory.create_eldar,
            EnemyFactory.create_tau,
        ]
        return random.choice(enemy_types)()


class CombatEngine:
    """Движок боя"""
    
    @staticmethod
    def perform_attack(attacker: Character, defender: Character) -> CombatResult:
        """
        Выполняет атаку
        
        Args:
            attacker: Атакующий персонаж
            defender: Защищающийся персонаж
            
        Returns:
            Результат боя
        """
        dice_roll = roll_dice()
        
        attack_success = dice_roll >= 3
        damage = 0
        
        if attack_success:
            damage = attacker.attack_power + dice_roll
            defender.health = max(0, defender.health - damage)
        
        defender_health_after = defender.health
        is_defender_defeated = defender_health_after <= 0
        
        return CombatResult(
            attacker=attacker,
            defender=defender,
            dice_roll=dice_roll,
            damage=damage,
            defender_health_after=defender_health_after,
            is_defender_defeated=is_defender_defeated
        )
    
    @staticmethod
    def generate_combat_situation(attacker: Character, defender: Character, dice_roll: int, is_successful: bool) -> str:
        """
        Генерирует описание ситуации боя для AI
        
        Args:
            attacker: Атакующий
            defender: Защищающийся
            dice_roll: Результат броска кубика
            is_successful: Успешна ли атака
            
        Returns:
            Описание ситуации
        """
        attacker_name = attacker.name
        defender_name = defender.name
        attacker_type = attacker.character_type.value if hasattr(attacker.character_type, 'value') else str(attacker.character_type)
        defender_type = defender.character_type.value if hasattr(defender.character_type, 'value') else str(defender.character_type)
        
        if is_successful:
            return (
                f"{attacker_name} ({attacker_type}) атакует {defender_name} ({defender_type}) "
                f"с результатом кубика {dice_roll}. Атака успешна! Нанесен урон."
            )
        else:
            return (
                f"{attacker_name} ({attacker_type}) атакует {defender_name} ({defender_type}) "
                f"с результатом кубика {dice_roll}. Атака промахнулась!"
            )


class GameManager:
    """Менеджер игры"""
    
    @staticmethod
    def create_new_game(space_marine_name: str = "Space Marine", num_enemies: int = 3) -> GameState:
        """
        Создает новую игру
        
        Args:
            space_marine_name: Имя Space Marine
            num_enemies: Количество врагов
            
        Returns:
            Начальное состояние игры
        """
        space_marine = SpaceMarine(
            name=space_marine_name,
            character_type=CharacterType.SPACE_MARINE,
            health=100,
            max_health=100,
            attack_power=6
        )
        
        enemies = [EnemyFactory.create_random_enemy() for _ in range(num_enemies)]
        
        return GameState(
            space_marine=space_marine,
            enemies=enemies,
            current_enemy_index=0,
            round_number=1,
            is_game_over=False,
            is_victory=False
        )
    
    @staticmethod
    def update_game_state(game_state: GameState, combat_result: CombatResult) -> GameState:
        """
        Обновляет состояние игры после боя
        
        Args:
            game_state: Текущее состояние игры
            combat_result: Результат боя
            
        Returns:
            Обновленное состояние игры
        """
        current_enemy = game_state.current_enemy
        
        if not current_enemy:
            game_state.is_game_over = True
            game_state.is_victory = True
            return game_state
        
        if combat_result.is_defender_defeated:
            game_state.current_enemy_index += 1
            
            if game_state.current_enemy_index >= len(game_state.enemies):
                game_state.is_game_over = True
                game_state.is_victory = True
        else:
            game_state.round_number += 1
        
        if game_state.space_marine.health <= 0:
            game_state.is_game_over = True
            game_state.is_victory = False
        
        return game_state
