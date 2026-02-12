"""
Клиент для OpenRouter API
"""
import os
import httpx
from typing import Optional
from dotenv import load_dotenv

from src.schemas import CharacterType

load_dotenv()

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_KEY = os.getenv("OPENROUTER_KEY")

# Экспортируем для health check
__all__ = ['generate_shout', 'OPENROUTER_KEY']


def generate_shout(character_type: CharacterType, situation: str, dice_roll: int, is_attack_successful: bool) -> str:
    """
    Генерирует крик персонажа через OpenRouter API
    
    Args:
        character_type: Тип персонажа
        situation: Описание ситуации боя
        dice_roll: Результат броска кубика
        is_attack_successful: Успешна ли атака
        
    Returns:
        Сгенерированный крик персонажа
        
    Raises:
        ValueError: Если OPENROUTER_KEY не установлен
        httpx.HTTPError: При ошибке запроса к API
    """
    if not OPENROUTER_KEY:
        print('[-] WARNING: no key!')
        # Fallback на предопределенные крики если ключ не установлен
        return _get_fallback_shout(character_type, is_attack_successful)
    
    character_descriptions = {
        CharacterType.SPACE_MARINE: "Space Marine из Warhammer 40k, кричит боевые кличи на латыни и английском",
        CharacterType.ORK: "Орк из Warhammer 40k, кричит на оркском языке, грубо и агрессивно",
        CharacterType.CHAOS_CULTIST: "Культист Хаоса из Warhammer 40k, кричит проклятия и призывы к темным силам",
        CharacterType.TYRANID: "Тиранид из Warhammer 40k, издает биологические звуки и рев",
        CharacterType.NECRON: "Некрон из Warhammer 40k, говорит механическим голосом, холодно и безэмоционально",
        CharacterType.ELDAR: "Эльдар из Warhammer 40k, говорит изысканно и элегантно",
        CharacterType.TAU: "Тау из Warhammer 40k, говорит формально и дисциплинированно"
    }
    
    result_text = "успешно атакует" if is_attack_successful else "промахивается"
    
    prompt = f"""Ты {character_descriptions.get(character_type, "персонаж")}.

Ситуация: {situation}
Результат броска кубика: {dice_roll}
Результат атаки: {result_text}

Напиши короткий крик (1-2 предложения максимум), который этот персонаж издает в этой ситуации. 
Крик должен соответствовать характеру персонажа и ситуации. Без дополнительных объяснений, только крик."""

    try:
        response = httpx.post(
            OPENROUTER_API_URL,
            headers={
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/python-course",
                "X-Title": "Space Marine Game",
            },
            json={
                "model": "google/gemma-3n-e2b-it:free",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 100,
            },
            timeout=30.0
        )
        # Проверяем статус, но не выбрасываем исключение - используем fallback
        if response.status_code != 200:
            print("[-] RESPONSE FAILED", response)
            return _get_fallback_shout(character_type, is_attack_successful)
        
        result = response.json()
        print(result)
        shout = result.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        
        if not shout:
            return _get_fallback_shout(character_type, is_attack_successful)
        
        return shout
        
    except httpx.HTTPStatusError as e:
        # Fallback на предопределенные крики при ошибке API
        return _get_fallback_shout(character_type, is_attack_successful)
    except httpx.RequestError as e:
        # Fallback на предопределенные крики при ошибке запроса
        return _get_fallback_shout(character_type, is_attack_successful)
    except Exception as e:
        # Fallback на предопределенные крики при любой другой ошибке
        return _get_fallback_shout(character_type, is_attack_successful)


def _get_fallback_shout(character_type: CharacterType, is_attack_successful: bool) -> str:
    """Предопределенные крики как fallback"""
    fallback_shouts = {
        CharacterType.SPACE_MARINE: {
            True: "FOR THE EMPEROR! PURGE THE XENOS!",
            False: "By the Throne! I shall not fail!"
        },
        CharacterType.ORK: {
            True: "WAAAGH! SMASH 'EM GOOD!",
            False: "OI! DAT AIN'T RIGHT!"
        },
        CharacterType.CHAOS_CULTIST: {
            True: "BLOOD FOR THE BLOOD GOD! SKULLS FOR THE SKULL THRONE!",
            False: "The Dark Gods will grant me strength!"
        },
        CharacterType.TYRANID: {
            True: "*SCREECHING ROAR* *BIOLOGICAL HORROR SOUNDS*",
            False: "*HISSING* *ALIEN GROWL*"
        },
        CharacterType.NECRON: {
            True: "Target eliminated. Proceeding to next objective.",
            False: "Recalibrating targeting systems."
        },
        CharacterType.ELDAR: {
            True: "By Asuryan's grace, the enemy falls!",
            False: "The strands of fate shift... I must adapt."
        },
        CharacterType.TAU: {
            True: "For the Greater Good! Eliminate the threat!",
            False: "Tactical reassessment required."
        }
    }
    
    return fallback_shouts.get(character_type, {}).get(is_attack_successful, "Battle cry!")
