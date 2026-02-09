# FastAPI Example - Пошаговое объяснение

## Общее описание

Этот пример демонстрирует создание веб-API на FastAPI для получения информации о пользователях GitHub. Приложение использует асинхронные запросы (async/await) и валидацию данных через Pydantic.

## Структура и компоненты

### 1. Импорты и инициализация

```python
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="GitHub Info API", version="1.0.0")
```

**Что делается:**
- `httpx` - асинхронная библиотека для HTTP-запросов (аналог `requests`, но с async/await)
- `FastAPI` - современный веб-фреймворк с автоматической документацией
- `HTTPException` - класс для обработки HTTP-ошибок
- `BaseModel` из Pydantic - для валидации и сериализации данных
- `Optional` - для опциональных полей в моделях
- `app = FastAPI(...)` - создание приложения с метаданными

**Зачем:**
- FastAPI использует async/await для высокой производительности
- Pydantic обеспечивает автоматическую валидацию данных
- Автоматическая генерация документации (Swagger/OpenAPI)

**Отличия от Flask/Django:**
- Асинхронная обработка запросов из коробки
- Автоматическая валидация через типы Python
- Автоматическая документация API

### 2. Pydantic модель - UserInfo

```python
class UserInfo(BaseModel):
    """Информация о пользователе GitHub"""
    login: str
    name: Optional[str] = None
    bio: Optional[str] = None
    public_repos: int
    followers: int
    following: int
    location: Optional[str] = None
```

**Что делается:**
- Создается модель данных, наследующаяся от `BaseModel`
- Поля с типами: `str`, `int`, `Optional[str]`
- `Optional[str] = None` - поле может быть None или строкой

**Зачем:**
- **Валидация:** FastAPI автоматически проверяет типы данных
- **Сериализация:** Автоматическое преобразование в JSON
- **Документация:** Поля модели попадают в Swagger-документацию
- **Type hints:** IDE может проверять типы

**Как работает:**
- При возврате `UserInfo` из функции, FastAPI автоматически сериализует в JSON
- При получении данных FastAPI валидирует их по модели
- Если данные не соответствуют модели - возвращается ошибка 422

### 3. Root endpoint - Главная страница

```python
@app.get("/")
async def root():
    return {
        "message": "GitHub Info API",
        "endpoints": {...}
    }
```

**Что делается:**
- `@app.get("/")` - декоратор для GET-запроса на корневой путь
- `async def` - асинхронная функция
- Возвращается обычный словарь (FastAPI автоматически преобразует в JSON)

**Зачем:**
- Документация API прямо в приложении
- Показывает доступные эндпоинты

**Отличие от Flask:**
- В Flask нужно `jsonify()`, в FastAPI можно просто вернуть dict
- Функция асинхронная (`async def`), что позволяет использовать `await`

### 4. Health Check - Проверка здоровья

```python
@app.get("/health")
async def health_check():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.github.com",
                timeout=5.0
            )
            github_available = response.status_code == 200
    except Exception:
        github_available = False
    
    return {
        "status": "healthy",
        "github_api_available": github_available
    }
```

**Что делается пошагово:**

1. **Асинхронный HTTP-клиент:**
   ```python
   async with httpx.AsyncClient() as client:
   ```
   - `httpx.AsyncClient()` - создает асинхронный HTTP-клиент
   - `async with` - контекстный менеджер для автоматического закрытия соединения
   - Аналог `requests`, но с поддержкой async/await

2. **Асинхронный запрос:**
   ```python
   response = await client.get("https://api.github.com", timeout=5.0)
   ```
   - `await` - ожидание завершения запроса
   - Пока запрос выполняется, сервер может обрабатывать другие запросы
   - Это ключевое преимущество асинхронности

3. **Проверка доступности:**
   - Если статус 200 - API доступен
   - При любой ошибке - API недоступен

**Зачем async/await:**
- **Производительность:** Сервер не блокируется во время ожидания ответа от внешнего API
- **Масштабируемость:** Может обрабатывать тысячи одновременных запросов
- **Эффективность:** Один поток может обрабатывать множество запросов

**Сравнение с синхронным кодом:**
```python
# Синхронно (блокирует поток)
response = requests.get("https://api.github.com")  # Ждем ответа

# Асинхронно (не блокирует)
response = await client.get("https://api.github.com")  # Можем обрабатывать другие запросы
```

### 5. Get User Info - Получение информации о пользователе

```python
@app.get("/user/{username}", response_model=UserInfo)
async def get_user_info(username: str):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.github.com/users/{username}",
                timeout=10.0
            )
            
            if response.status_code == 404:
                raise HTTPException(
                    status_code=404,
                    detail=f"Пользователь {username} не найден"
                )
            
            response.raise_for_status()
            data = response.json()
            
            return UserInfo(
                login=data.get("login", username),
                name=data.get("name"),
                bio=data.get("bio"),
                public_repos=data.get("public_repos", 0),
                followers=data.get("followers", 0),
                following=data.get("following", 0),
                location=data.get("location")
            )
```

**Что делается пошагово:**

1. **Параметры пути:**
   ```python
   @app.get("/user/{username}")
   async def get_user_info(username: str):
   ```
   - `{username}` в URL извлекается и передается как параметр функции
   - `username: str` - тип аннотация, FastAPI валидирует тип
   - Пример: `/user/octocat` → `username = "octocat"`

2. **Response model:**
   ```python
   response_model=UserInfo
   ```
   - Указывает, что ответ должен соответствовать модели `UserInfo`
   - FastAPI автоматически валидирует и сериализует ответ
   - Попадает в документацию Swagger

3. **Асинхронный запрос к GitHub API:**
   - Формируется URL: `https://api.github.com/users/{username}`
   - Делается GET-запрос с таймаутом
   - `await` позволяет не блокировать сервер

4. **Обработка ошибок:**

   **404 - Пользователь не найден:**
   ```python
   if response.status_code == 404:
       raise HTTPException(status_code=404, detail="...")
   ```
   - `HTTPException` - специальный класс FastAPI для HTTP-ошибок
   - Автоматически преобразуется в правильный JSON-ответ с статус-кодом

   **Другие HTTP-ошибки:**
   ```python
   except httpx.HTTPStatusError as e:
       raise HTTPException(status_code=e.response.status_code, ...)
   ```
   - Обрабатываются ошибки HTTP (400, 500 и т.д.)

   **Ошибки сети:**
   ```python
   except httpx.RequestError as e:
       raise HTTPException(status_code=503, ...)
   ```
   - Обрабатываются ошибки соединения (таймауты, DNS и т.д.)

5. **Создание модели из данных:**
   ```python
   return UserInfo(
       login=data.get("login", username),
       name=data.get("name"),
       ...
   )
   ```
   - Создается экземпляр `UserInfo` из данных GitHub API
   - `data.get()` - безопасное извлечение с fallback-значениями
   - FastAPI автоматически сериализует модель в JSON

**Зачем response_model:**
- Гарантирует, что ответ соответствует схеме
- Автоматическая валидация данных
- Улучшает документацию API
- Помогает IDE с автодополнением

### 6. Запуск приложения

```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Что делается:**
- `uvicorn` - ASGI-сервер для запуска FastAPI
- ASGI (Asynchronous Server Gateway Interface) - протокол для асинхронных приложений
- Аналог WSGI, но для async/await

**Зачем uvicorn:**
- FastAPI требует ASGI-сервер (не может работать с обычным WSGI)
- uvicorn - один из самых быстрых ASGI-серверов
- Поддерживает async/await из коробки

## Основные концепции FastAPI

### 1. Асинхронность (async/await)

```python
async def function():
    response = await some_async_operation()
    return response
```

**Преимущества:**
- Не блокирует поток во время ожидания I/O операций
- Может обрабатывать множество запросов одновременно
- Высокая производительность при работе с внешними API

**Когда использовать:**
- HTTP-запросы к внешним API
- Работа с базами данных (async драйверы)
- Файловые операции (async версии)

### 2. Валидация через Pydantic

```python
class UserInfo(BaseModel):
    login: str  # Обязательное поле
    name: Optional[str] = None  # Опциональное поле
```

**Автоматическая валидация:**
- FastAPI проверяет типы автоматически
- Если тип неверный - возвращается 422 Unprocessable Entity
- Не нужно писать валидацию вручную

### 3. Параметры пути и запроса

```python
@app.get("/user/{username}")
async def get_user(username: str, limit: int = 10):
    ...
```

- `{username}` - параметр пути (обязательный)
- `limit: int = 10` - параметр запроса (опциональный, со значением по умолчанию)
- Пример: `/user/octocat?limit=20`

### 4. HTTPException

```python
raise HTTPException(status_code=404, detail="Not found")
```

- Специальный класс для HTTP-ошибок
- Автоматически преобразуется в JSON-ответ
- Правильные заголовки и статус-код

### 5. Автоматическая документация

FastAPI автоматически генерирует:
- **Swagger UI:** `/docs` - интерактивная документация
- **ReDoc:** `/redoc` - альтернативная документация
- **OpenAPI схема:** `/openapi.json` - JSON-схема API

**Зачем:**
- Не нужно писать документацию вручную
- Можно тестировать API прямо в браузере
- Всегда актуальная документация

## Примеры использования

1. **Получить информацию о пользователе:**
   ```
   GET /user/octocat
   Ответ: {"login": "octocat", "name": "The Octocat", "public_repos": 8, ...}
   ```

2. **Проверить здоровье:**
   ```
   GET /health
   Ответ: {"status": "healthy", "github_api_available": true}
   ```

3. **Автоматическая документация:**
   ```
   GET /docs
   Открывается Swagger UI с полной документацией
   ```

## Сравнение с Flask и Django

| Особенность | FastAPI | Flask | Django |
|------------|---------|-------|--------|
| Асинхронность | ✅ Встроенная | ❌ Требует расширения | ✅ Django 3.1+ |
| Валидация | ✅ Автоматическая (Pydantic) | ❌ Вручную | ✅ Forms/Serializers |
| Документация | ✅ Автоматическая | ❌ Вручную | ❌ Вручную |
| Производительность | ⚡ Очень высокая | ⚡ Высокая | ⚡ Высокая |
| Простота | ✅ Простой | ✅ Очень простой | ⚠️ Сложнее |

## Итоги

Этот пример демонстрирует:
- Создание REST API на FastAPI
- Асинхронные HTTP-запросы через `httpx`
- Валидацию данных через Pydantic модели
- Обработку ошибок через HTTPException
- Автоматическую генерацию документации
- Использование async/await для высокой производительности

FastAPI идеально подходит для:
- Высоконагруженных API
- Микросервисов
- Приложений с множеством внешних API-вызовов
- Проектов, где важна автоматическая документация
