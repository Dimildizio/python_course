# Объяснение структуры src/ - Space Marine Game

## Общее описание

Директория `src/` содержит код игры Space Marine - веб-приложение на FastAPI, где Space Marine сражается с врагами из вселенной Warhammer 40k. Игра использует AI (OpenRouter) для генерации боевых криков персонажей.

## Архитектура проекта

Проект следует принципам модульной архитектуры:
- **Разделение ответственности:** каждый файл отвечает за свою область
- **Композиция:** компоненты работают вместе, но независимы
- **Тестируемость:** каждый модуль можно тестировать отдельно

## Структура файлов

```
src/
├── main.py              # Точка входа, FastAPI приложение
├── game_logic.py        # Бизнес-логика игры
├── schemas.py           # Модели данных (Pydantic)
├── openrouter_client.py # Клиент для AI API
└── combat_logger.py     # Логирование боевых действий
```

---

## 1. schemas.py - Модели данных

### Назначение
Определяет структуру данных игры через Pydantic модели. Обеспечивает валидацию и типизацию.

### Компоненты

#### CharacterType - Enum типов персонажей
```python
class CharacterType(str, Enum):
    SPACE_MARINE = "space_marine"
    ORK = "ork"
    CHAOS_CULTIST = "chaos_cultist"
    ...
```

**Что делается:**
- Определяет все возможные типы персонажей
- Использует Enum для ограничения допустимых значений
- Наследуется от `str` для удобной сериализации

**Зачем:**
- Типобезопасность: нельзя создать персонажа с несуществующим типом
- Валидация: FastAPI автоматически проверяет соответствие
- Документация: попадает в Swagger

#### Character - Базовый класс персонажа
```python
class Character(BaseModel):
    name: str
    character_type: CharacterType
    health: int = Field(ge=0)
    max_health: int = Field(ge=1)
    attack_power: int = Field(ge=1)
```

**Что делается:**
- Базовый класс для всех персонажей
- `Field(ge=0)` - валидация: значение >= 0
- Определяет общие свойства всех персонажей

**Зачем:**
- Единая структура данных
- Автоматическая валидация (здоровье не может быть отрицательным)
- Переиспользование кода

#### Enemy и SpaceMarine - Специализированные классы
```python
class Enemy(Character):
    pass

class SpaceMarine(Character):
    character_type: CharacterType = CharacterType.SPACE_MARINE
```

**Что делается:**
- Наследуются от `Character`
- `SpaceMarine` фиксирует тип персонажа
- Можно добавить специфичные поля в будущем

**Зачем:**
- Семантическое разделение: враг vs игрок
- Возможность расширения без изменения базового класса

#### CombatResult - Результат боя
```python
class CombatResult(BaseModel):
    attacker: Character
    defender: Character
    dice_roll: int = Field(ge=1, le=6)
    damage: int = Field(ge=0)
    defender_health_after: int = Field(ge=0)
    is_defender_defeated: bool
```

**Что делается:**
- Хранит результат одного раунда боя
- `Field(ge=1, le=6)` - валидация: значение от 1 до 6 (бросок кубика)
- Содержит всю информацию о результате атаки

**Зачем:**
- Структурированное хранение результатов
- Валидация данных (кубик не может выдать 7)
- Удобная передача данных между компонентами

#### GameState - Состояние игры
```python
class GameState(BaseModel):
    space_marine: SpaceMarine
    enemies: List[Enemy]
    current_enemy_index: int = Field(ge=0)
    round_number: int = Field(ge=1)
    is_game_over: bool = False
    is_victory: bool = False
    
    @property
    def current_enemy(self) -> Optional[Enemy]:
        ...
```

**Что делается:**
- Хранит полное состояние игры
- `@property` - вычисляемое свойство для текущего врага
- Инкапсулирует всю логику состояния

**Зачем:**
- Единая точка доступа к состоянию игры
- Удобное получение текущего врага через свойство
- Валидация индексов и значений

---

## 2. game_logic.py - Бизнес-логика игры

### Назначение
Содержит всю игровую логику, отделенную от веб-слоя. Можно использовать без FastAPI.

### Компоненты

#### roll_dice() - Бросок кубика
```python
def roll_dice(sides: int = 6) -> int:
    return random.randint(1, sides)
```

**Что делается:**
- Генерирует случайное число от 1 до 6
- Простая функция для генерации случайности

**Зачем:**
- Централизованная генерация случайных чисел
- Легко тестировать (можно мокировать)
- Можно изменить логику в одном месте

#### EnemyFactory - Фабрика врагов
```python
class EnemyFactory:
    @staticmethod
    def create_ork(name: str = "Ork Boy") -> Enemy:
        return Enemy(...)
    
    @staticmethod
    def create_random_enemy() -> Enemy:
        ...
```

**Что делается:**
- Статические методы для создания разных типов врагов
- Каждый метод создает врага с предустановленными характеристиками
- `create_random_enemy()` создает случайного врага

**Зачем:**
- **Паттерн Factory:** централизованное создание объектов
- Легко добавлять новые типы врагов
- Консистентные характеристики для каждого типа
- Упрощает тестирование

**Пример использования:**
```python
ork = EnemyFactory.create_ork()
random_enemy = EnemyFactory.create_random_enemy()
```

#### CombatEngine - Движок боя
```python
class CombatEngine:
    @staticmethod
    def perform_attack(attacker: Character, defender: Character) -> CombatResult:
        dice_roll = roll_dice()
        attack_success = dice_roll >= 3
        damage = 0
        
        if attack_success:
            damage = attacker.attack_power + dice_roll
            defender.health = max(0, defender.health - damage)
        
        return CombatResult(...)
```

**Что делается пошагово:**

1. **Бросок кубика:**
   - Генерируется случайное число от 1 до 6

2. **Проверка успешности атаки:**
   - Если кубик >= 3 - атака успешна
   - Это простая механика: 50% шанс успеха

3. **Расчет урона:**
   - Урон = сила атаки + результат кубика
   - Пример: attack_power=6, dice=4 → урон=10

4. **Применение урона:**
   - Вычитается из здоровья защитника
   - `max(0, ...)` гарантирует, что здоровье не станет отрицательным

5. **Создание результата:**
   - Возвращается `CombatResult` со всей информацией

**Зачем отдельный класс:**
- Изоляция игровой логики
- Легко тестировать боевую механику
- Можно изменить правила боя в одном месте
- Не зависит от веб-фреймворка

#### generate_combat_situation() - Описание ситуации
```python
def generate_combat_situation(attacker, defender, dice_roll, is_successful) -> str:
    if is_successful:
        return f"{attacker_name} атакует {defender_name} ..."
```

**Что делается:**
- Генерирует текстовое описание боевой ситуации
- Используется для создания промпта для AI

**Зачем:**
- AI нужен контекст для генерации крика
- Централизованное форматирование описаний

#### GameManager - Менеджер игры
```python
class GameManager:
    @staticmethod
    def create_new_game(space_marine_name: str, num_enemies: int) -> GameState:
        space_marine = SpaceMarine(...)
        enemies = [EnemyFactory.create_random_enemy() for _ in range(num_enemies)]
        return GameState(...)
    
    @staticmethod
    def update_game_state(game_state: GameState, combat_result: CombatResult) -> GameState:
        ...
```

**Что делается:**

1. **create_new_game():**
   - Создает Space Marine с начальными характеристиками
   - Генерирует список случайных врагов
   - Инициализирует состояние игры

2. **update_game_state():**
   - Обновляет состояние после боя
   - Проверяет условия победы/поражения
   - Переходит к следующему врагу при победе над текущим

**Зачем:**
- Централизованное управление состоянием игры
- Четкая логика перехода между состояниями
- Легко тестировать игровую логику

---

## 3. openrouter_client.py - Клиент для AI API

### Назначение
Интеграция с OpenRouter API для генерации боевых криков персонажей через AI.

### Компоненты

#### Конфигурация
```python
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_KEY = os.getenv("OPENROUTER_KEY")
```

**Что делается:**
- Загружает API ключ из переменных окружения (`.env`)
- Определяет URL API

**Зачем:**
- Безопасность: ключ не хранится в коде
- Гибкость: можно менять без изменения кода

#### generate_shout() - Генерация крика
```python
def generate_shout(character_type: CharacterType, situation: str, 
                   dice_roll: int, is_attack_successful: bool) -> str:
    if not OPENROUTER_KEY:
        return _get_fallback_shout(character_type, is_attack_successful)
    
    prompt = f"""Ты {character_descriptions[character_type]}.
    Ситуация: {situation}
    ...
    """
    
    response = httpx.post(OPENROUTER_API_URL, ...)
    return shout
```

**Что делается пошагово:**

1. **Проверка ключа:**
   - Если ключ не установлен - возвращается fallback-крик
   - Это позволяет работать без API ключа

2. **Формирование промпта:**
   - Описывается персонаж и ситуация
   - AI получает контекст для генерации крика

3. **Запрос к API:**
   - Используется `httpx` для асинхронных запросов
   - Модель: `google/gemini-2.5-flash-lite`
   - Ограничение: максимум 100 токенов (короткий крик)

4. **Обработка ошибок:**
   - При любой ошибке возвращается fallback-крик
   - Игра продолжает работать даже при недоступности API

**Зачем:**
- Динамическая генерация контента
- Уникальные крики для каждой ситуации
- Fallback гарантирует работоспособность

#### _get_fallback_shout() - Резервные крики
```python
def _get_fallback_shout(character_type: CharacterType, is_attack_successful: bool) -> str:
    fallback_shouts = {
        CharacterType.SPACE_MARINE: {
            True: "FOR THE EMPEROR! PURGE THE XENOS!",
            False: "By the Throne! I shall not fail!"
        },
        ...
    }
```

**Что делается:**
- Предопределенные крики для каждого типа персонажа
- Разные крики для успешной/неуспешной атаки

**Зачем:**
- Гарантирует работу без AI
- Быстрый ответ (не нужно ждать API)
- Соответствие тематике Warhammer 40k

---

## 4. combat_logger.py - Логирование

### Назначение
Настройка и функции для логирования боевых действий в файл.

### Компоненты

#### setup_combat_logger() - Настройка логгера
```python
def setup_combat_logger():
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / f"combat_{datetime.now().strftime('%Y%m%d')}.log"
    
    logger = logging.getLogger("combat")
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    ...
```

**Что делается:**
- Создает директорию `logs/` если её нет
- Создает файл лога с датой в имени: `combat_20260209.log`
- Настраивает формат: время, уровень, сообщение
- Использует кодировку UTF-8 для русских символов

**Зачем:**
- Отдельные логи для каждого дня
- Структурированное логирование
- Легко найти логи по дате

#### Функции логирования
```python
def log_game_start(logger, space_marine_name: str, num_enemies: int):
    logger.info("=" * 60)
    logger.info(f"НАЧАЛО ИГРЫ - Space Marine: {space_marine_name}, Врагов: {num_enemies}")
    logger.info("=" * 60)

def log_shout(logger, character_name: str, character_type: str, shout: str):
    logger.info(f"{character_name} ({character_type}) кричит: \"{shout}\"")

def log_game_end(logger, is_victory: bool, final_round: int):
    ...
```

**Что делается:**
- Специализированные функции для разных событий
- Форматирование сообщений для читаемости
- Разделители для визуального выделения

**Зачем:**
- Структурированное логирование
- Легко анализировать логи
- Отладка игровых механик

---

## 5. main.py - Точка входа, FastAPI приложение

### Назначение
Объединяет все компоненты в веб-приложение. Содержит API эндпоинты и оркестрацию игры.

### Компоненты

#### Глобальное состояние
```python
current_game: Optional[Dict[str, Any]] = None
combat_count: int = 0
combat_logger = setup_combat_logger()
```

**Что делается:**
- Хранит текущее состояние игры в памяти
- Счетчик боев для статистики
- Инициализирует логгер при старте

**Зачем:**
- Простое хранилище состояния (в production используют БД)
- Быстрый доступ к текущей игре

**Ограничения:**
- Состояние теряется при перезапуске
- Не работает при нескольких экземплярах сервера
- Для production нужна БД или Redis

#### Вспомогательные функции
```python
def roll_dice(sides: int = 6) -> int:
    return random.randint(1, sides)

def create_enemy(enemy_type: str) -> Dict[str, Any]:
    enemies_config = {...}
    ...
```

**Что делается:**
- Дублирует функции из `game_logic.py` для совместимости
- Использует словари вместо Pydantic моделей (упрощенная версия)

**Зачем:**
- Совместимость со старым кодом
- Упрощенная версия для демонстрации

#### POST /game/start - Начать игру
```python
@app.post("/game/start")
async def start_game(space_marine_name: str = "Space Marine", num_enemies: int = 3):
    global current_game, combat_count
    
    current_game = {
        "space_marine": {...},
        "enemies": [create_enemy(...) for _ in range(num_enemies)],
        "current_enemy_index": 0,
        "round_number": 1,
        ...
    }
    
    log_game_start(combat_logger, space_marine_name, num_enemies)
    return current_game
```

**Что делается:**
- Создает новую игру с указанными параметрами
- Генерирует Space Marine и список врагов
- Инициализирует состояние игры
- Логирует начало игры

**Зачем:**
- REST API для начала игры
- Параметризуемая настройка (имя, количество врагов)

#### POST /game/combat - Выполнить бой
```python
@app.post("/game/combat")
async def perform_combat():
    # Проверки состояния игры
    # Бросок кубика и атака
    # Генерация крика через AI
    # Обновление состояния
    # Логирование
    return result
```

**Что делается пошагово:**

1. **Валидация состояния:**
   - Проверяет, начата ли игра
   - Проверяет, не окончена ли игра
   - Проверяет наличие врагов

2. **Выполнение боя:**
   - Бросок кубика
   - Расчет урона
   - Применение урона к врагу

3. **Генерация крика:**
   - Если атака успешна - генерируется крик через AI
   - Используется `openrouter_client.generate_shout()`
   - Логируется крик

4. **Обновление состояния:**
   - Если враг побежден - переход к следующему
   - Если все враги побеждены - победа
   - Если Space Marine мертв - поражение

5. **Логирование:**
   - Записывается информация о раунде
   - Результаты боя

**Зачем:**
- REST API для выполнения хода
- Интеграция всех компонентов
- Возврат детальной информации о бое

#### GET /game/stats - Статистика
```python
@app.get("/game/stats")
async def get_stats():
    return {
        "combat_count": combat_count,
        "game_active": not current_game["is_game_over"],
        "round_number": current_game["round_number"],
        ...
    }
```

**Что делается:**
- Возвращает текущую статистику игры
- Количество боев, раунд, здоровье, оставшиеся враги

**Зачем:**
- Мониторинг состояния игры
- Отладка и анализ

#### GET /health - Health check
```python
@app.get("/health")
async def health_check():
    is_openrouter_available = OPENROUTER_KEY is not None and OPENROUTER_KEY != ""
    return {
        "status": "healthy",
        "openrouter_available": is_openrouter_available,
        ...
    }
```

**Что делается:**
- Проверяет доступность OpenRouter API
- Возвращает статус сервиса

**Зачем:**
- Мониторинг работоспособности
- Проверка зависимостей

---

## Архитектурные принципы

### 1. Разделение ответственности
- **schemas.py** - только модели данных
- **game_logic.py** - только игровая логика
- **openrouter_client.py** - только работа с AI API
- **combat_logger.py** - только логирование
- **main.py** - только веб-слой и оркестрация

### 2. Композиция
- Компоненты работают вместе, но независимы
- Можно заменить один компонент без изменения других
- Легко тестировать каждый компонент отдельно

### 3. Расширяемость
- Легко добавить новые типы врагов (EnemyFactory)
- Легко изменить правила боя (CombatEngine)
- Легко добавить новые эндпоинты (main.py)

### 4. Обработка ошибок
- Fallback на предопределенные крики при ошибках AI
- Валидация через Pydantic
- HTTPException для веб-ошибок

## Потоки данных

### Начало игры:
```
Client → POST /game/start → main.py → create_enemy() → GameState → Response
```

### Выполнение боя:
```
Client → POST /game/combat → main.py → roll_dice() → 
  → calculate_damage() → openrouter_client.generate_shout() → 
  → update_state() → combat_logger → Response
```

### Получение статистики:
```
Client → GET /game/stats → main.py → current_game → Response
```

## Итоги

Проект демонстрирует:
- Модульную архитектуру с четким разделением ответственности
- Использование Pydantic для валидации данных
- Интеграцию с внешними API (OpenRouter)
- Структурированное логирование
- REST API на FastAPI
- Обработку ошибок и fallback-механизмы
- Расширяемую структуру кода

Каждый файл имеет четкую роль и может развиваться независимо от других.
