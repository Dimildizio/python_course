# Space Marine -0.1 - FastAPI проект

Простой проект для изучения FastAPI с текстовой игрой.

## Быстрый старт

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Создайте `.env` файл:
```
OPENROUTER_KEY=your_key_here
```

3. Запустите сервер:
```bash
cd src
python main.py
```

API доступен на http://localhost:8000

## API Endpoints

### 1. Health Check
```bash
curl http://localhost:8000/health
```
Проверяет доступность сервиса и OpenRouter API.

### 2. Начать игру
```bash
curl -X POST "http://localhost:8000/game/start?space_marine_name=Brother%20Titkus&num_enemies=2"
```
Генерирует Space Marine и врагов, хранит в памяти.

### 3. Выполнить следующий ход
```bash
curl -X POST "http://localhost:8000/game/next_turn"
```
Space Marine атакует врага, затем враг автоматически атакует в ответ (если жив). В ответе есть крики обоих персонажей, если атаки успешны. Повторяйте пока игра не закончится.

### 4. Статистика
```bash
curl http://localhost:8000/game/stats
```
Показывает количество боев и состояние игры.

## Логирование

Все боевые действия логируются в `logs/combat_YYYYMMDD.log`

## Структура проекта

```
src/
  ├── main.py              # FastAPI приложение
  ├── openrouter_client.py # Клиент для OpenRouter API
  ├── combat_logger.py     # Логирование
  └── schemas.py           # Схемы (используются только для генерации криков)
```
