"""
FastAPI приложение для Space Marine игры
"""
from fastapi import FastAPI, HTTPException
from typing import Optional, Dict, Any
import random

from src.openrouter_client import generate_shout, OPENROUTER_KEY
from src.combat_logger import (
    setup_combat_logger, log_combat_result, 
    log_shout, log_game_start, log_game_end
)

app = FastAPI(title="Space Marine Game API", version="1.0.0")

# Хранилище игры в памяти
current_game: Optional[Dict[str, Any]] = None
combat_count: int = 0

# Настройка логгера
combat_logger = setup_combat_logger()


def roll_dice(sides: int = 6) -> int:
    """Бросок кубика"""
    return random.randint(1, sides)


def create_enemy(enemy_type: str) -> Dict[str, Any]:
    """Создает врага"""
    enemies_config = {
        "ork": {"name": "Ork Boy", "health": 30, "attack_power": 4},
        "chaos_cultist": {"name": "Chaos Cultist", "health": 20, "attack_power": 3},
        "tyranid": {"name": "Tyranid Warrior", "health": 35, "attack_power": 5},
        "necron": {"name": "Necron Warrior", "health": 25, "attack_power": 4},
        "eldar": {"name": "Eldar Guardian", "health": 22, "attack_power": 5},
        "tau": {"name": "Tau Fire Warrior", "health": 24, "attack_power": 4},
    }
    
    config = enemies_config.get(enemy_type, enemies_config["ork"])
    enemy_types = list(enemies_config.keys())
    selected_type = enemy_type if enemy_type in enemy_types else random.choice(enemy_types)
    
    return {
        "name": config["name"],
        "character_type": selected_type,
        "health": config["health"],
        "max_health": config["health"],
        "attack_power": config["attack_power"]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint - проверяет доступность OpenRouter"""
    is_openrouter_available = OPENROUTER_KEY is not None and OPENROUTER_KEY != ""
    
    return {
        "status": "healthy",
        "service": "space_marine_game",
        "openrouter_available": is_openrouter_available,
        "openrouter_key_set": is_openrouter_available
    }


@app.post("/game/start")
async def start_game(space_marine_name: str = "Space Marine", num_enemies: int = 3):
    """
    Начать новую игру - генерирует персонажа и врагов
    """
    global current_game, combat_count
    
    enemy_types = ["ork", "chaos_cultist", "tyranid", "necron", "eldar", "tau"]
    
    current_game = {
        "space_marine": {
            "name": space_marine_name,
            "character_type": "space_marine",
            "health": 100,
            "max_health": 100,
            "attack_power": 6
        },
        "enemies": [create_enemy(random.choice(enemy_types)) for _ in range(num_enemies)],
        "current_enemy_index": 0,
        "round_number": 1,
        "is_game_over": False,
        "is_victory": False
    }
    
    combat_count = 0
    
    log_game_start(combat_logger, space_marine_name, num_enemies)
    
    return current_game


@app.post("/game/next_turn")
async def perform_next_turn():
    """
    Выполнить следующий ход боя - Space Marine атакует, затем враг автоматически атакует в ответ (если жив)
    """
    global current_game, combat_count
    
    if not current_game:
        raise HTTPException(status_code=400, detail="Игра не начата. Вызовите /game/start")
    
    if current_game["is_game_over"]:
        raise HTTPException(status_code=400, detail="Игра уже окончена")
    
    current_enemy_index = current_game["current_enemy_index"]
    if current_enemy_index >= len(current_game["enemies"]):
        raise HTTPException(status_code=400, detail="Нет врагов для боя")
    
    current_enemy = current_game["enemies"][current_enemy_index]
    space_marine = current_game["space_marine"]
    
    result = {
        "player_attack": {},
        "enemy_attack": None
    }
    
    # Атака Space Marine
    dice_roll = roll_dice()
    attack_success = dice_roll >= 3
    damage = 0
    
    if attack_success:
        damage = space_marine["attack_power"] + dice_roll
        current_enemy["health"] = max(0, current_enemy["health"] - damage)
    
    defender_health_after = current_enemy["health"]
    is_defender_defeated = defender_health_after <= 0
    
    combat_count += 1
    
    # Логируем атаку Space Marine
    round_num = current_game["round_number"]
    log_message = (
        f"Раунд {round_num} - {space_marine['name']} ({space_marine['character_type']}) "
        f"атакует {current_enemy['name']} ({current_enemy['character_type']}). "
        f"Бросок кубика: {dice_roll}, Урон: {damage}, "
        f"HP защитника: {defender_health_after}/{current_enemy['max_health']}"
    )
    if is_defender_defeated:
        log_message += f" - {current_enemy['name']} ПОБЕЖДЕН!"
    combat_logger.info(log_message)
    
    # Генерируем крик Space Marine если атака успешна
    player_shout = None
    if damage > 0:
        try:
            situation = (
                f"{space_marine['name']} ({space_marine['character_type']}) атакует "
                f"{current_enemy['name']} ({current_enemy['character_type']}) "
                f"с результатом кубика {dice_roll}. Атака успешна! Нанесен урон."
            )
            try:
                from src.schemas import CharacterType
                player_shout = generate_shout(
                    character_type=CharacterType.SPACE_MARINE,
                    situation=situation,
                    dice_roll=dice_roll,
                    is_attack_successful=True
                )
            except Exception:
                player_shout = "FOR THE EMPEROR!"
            log_shout(combat_logger, space_marine["name"], "space_marine", player_shout)
        except Exception:
            player_shout = "FOR THE EMPEROR!"
    
    result["player_attack"] = {
        "attacker": space_marine,
        "defender": current_enemy,
        "dice_roll": dice_roll,
        "damage": damage,
        "defender_health_after": defender_health_after,
        "is_defender_defeated": is_defender_defeated
    }
    if player_shout:
        result["player_attack"]["shout"] = player_shout
    
    # Если враг жив, он автоматически атакует в ответ
    if not is_defender_defeated and space_marine["health"] > 0:
        enemy_dice_roll = roll_dice()
        enemy_attack_success = enemy_dice_roll >= 3
        enemy_damage = 0
        
        if enemy_attack_success:
            enemy_damage = current_enemy["attack_power"] + enemy_dice_roll
            space_marine["health"] = max(0, space_marine["health"] - enemy_damage)
        
        space_marine_health_after = space_marine["health"]
        is_space_marine_defeated = space_marine_health_after <= 0
        
        # Логируем атаку врага
        enemy_log_message = (
            f"Раунд {round_num} - {current_enemy['name']} ({current_enemy['character_type']}) "
            f"атакует {space_marine['name']} ({space_marine['character_type']}). "
            f"Бросок кубика: {enemy_dice_roll}, Урон: {enemy_damage}, "
            f"HP защитника: {space_marine_health_after}/{space_marine['max_health']}"
        )
        if is_space_marine_defeated:
            enemy_log_message += f" - {space_marine['name']} ПОБЕЖДЕН!"
        combat_logger.info(enemy_log_message)
        
        # Генерируем крик врага если атака успешна
        enemy_shout = None
        if enemy_damage > 0:
            try:
                from src.schemas import CharacterType
                # Маппинг типов врагов из строк в enum
                enemy_type_mapping = {
                    "ork": CharacterType.ORK,
                    "chaos_cultist": CharacterType.CHAOS_CULTIST,
                    "tyranid": CharacterType.TYRANID,
                    "necron": CharacterType.NECRON,
                    "eldar": CharacterType.ELDAR,
                    "tau": CharacterType.TAU
                }
                enemy_character_type = enemy_type_mapping.get(
                    current_enemy["character_type"], 
                    CharacterType.ORK
                )
                situation = (
                    f"{current_enemy['name']} ({current_enemy['character_type']}) атакует "
                    f"{space_marine['name']} ({space_marine['character_type']}) "
                    f"с результатом кубика {enemy_dice_roll}. Атака успешна! Нанесен урон."
                )
                try:
                    enemy_shout = generate_shout(
                        character_type=enemy_character_type,
                        situation=situation,
                        dice_roll=enemy_dice_roll,
                        is_attack_successful=True
                    )
                except Exception:
                    enemy_shout = "Battle cry!"
                log_shout(combat_logger, current_enemy["name"], current_enemy["character_type"], enemy_shout)
            except Exception:
                enemy_shout = "Battle cry!"
        
        result["enemy_attack"] = {
            "attacker": current_enemy,
            "defender": space_marine,
            "dice_roll": enemy_dice_roll,
            "damage": enemy_damage,
            "defender_health_after": space_marine_health_after,
            "is_defender_defeated": is_space_marine_defeated
        }
        if enemy_shout:
            result["enemy_attack"]["shout"] = enemy_shout
    
    # Обновляем состояние игры
    if is_defender_defeated:
        current_game["current_enemy_index"] += 1
        if current_game["current_enemy_index"] >= len(current_game["enemies"]):
            current_game["is_game_over"] = True
            current_game["is_victory"] = True
            log_game_end(combat_logger, True, current_game["round_number"])
    elif space_marine["health"] <= 0:
        current_game["is_game_over"] = True
        current_game["is_victory"] = False
        log_game_end(combat_logger, False, current_game["round_number"])
    else:
        current_game["round_number"] += 1
    
    return result


@app.get("/game/stats")
async def get_stats():
    """
    Получить статистику по количеству боев
    """
    global current_game, combat_count
    
    if not current_game:
        return {
            "combat_count": 0,
            "game_active": False
        }
    
    enemies_remaining = len([e for e in current_game["enemies"] if e["health"] > 0])
    
    return {
        "combat_count": combat_count,
        "game_active": not current_game["is_game_over"],
        "round_number": current_game["round_number"],
        "space_marine_health": current_game["space_marine"]["health"],
        "enemies_remaining": enemies_remaining
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
