# Flask Example - Пошаговое объяснение

## Общее описание

Этот пример демонстрирует создание веб-API на Flask для получения курсов валют и конвертации между ними. Приложение использует внешний API (ExchangeRate API) и реализует простое кэширование для оптимизации запросов.

## Структура и компоненты

### 1. Импорты и инициализация

```python
import requests
from flask import Flask, jsonify
from datetime import datetime

app = Flask(__name__)
```

**Что делается:**
- `requests` - для HTTP-запросов к внешнему API
- `Flask` - веб-фреймворк
- `jsonify` - функция Flask для создания JSON-ответов
- `datetime` - для работы с временными метками кэша
- `app = Flask(__name__)` - создание экземпляра приложения Flask

**Зачем:**
- Базовые инструменты для создания веб-сервера и работы с API

### 2. Система кэширования

```python
_exchange_cache = {}
_cache_timestamp = None
CACHE_TTL = 3600  # 1 час
```

**Что делается:**
- `_exchange_cache` - словарь для хранения курсов валют
- `_cache_timestamp` - время последнего обновления кэша
- `CACHE_TTL` - время жизни кэша в секундах (3600 = 1 час)

**Зачем:**
- Кэширование уменьшает количество запросов к внешнему API
- Экономит время и ресурсы
- В реальных проектах используют Redis или Memcached
- Здесь используется простой in-memory кэш для демонстрации

### 3. Root endpoint - Главная страница

```python
@app.route("/")
def root():
    return jsonify({
        "message": "Currency Exchange API",
        "endpoints": {...}
    })
```

**Что делается:**
- `@app.route("/")` - декоратор, который связывает URL `/` с функцией `root()`
- `jsonify()` - преобразует Python-словарь в JSON-ответ с правильными заголовками
- Возвращает описание доступных эндпоинтов

**Зачем:**
- Документация API прямо в приложении
- Помогает пользователям понять, какие запросы можно делать

**Как работает декоратор `@app.route()`:**
- Flask использует декораторы для маршрутизации
- Когда приходит запрос на `/`, вызывается функция `root()`
- Результат функции автоматически преобразуется в HTTP-ответ

### 4. Health Check - Проверка здоровья

```python
@app.route("/health")
def health_check():
    try:
        response = requests.get(
            "https://api.exchangerate-api.com/v4/latest/USD",
            timeout=5
        )
        api_available = response.status_code == 200
    except Exception:
        api_available = False
    
    return jsonify({
        "status": "healthy",
        "exchange_api_available": api_available,
        "timestamp": datetime.now().isoformat()
    })
```

**Что делается пошагово:**

1. **Тестовый запрос:**
   - Делается запрос к внешнему API курсов валют
   - `timeout=5` - таймаут 5 секунд, чтобы не ждать долго

2. **Проверка доступности:**
   - Если статус ответа 200 - API доступен
   - Если произошла ошибка (Exception) - API недоступен

3. **Возврат статуса:**
   - Возвращается JSON с информацией о здоровье сервиса
   - Добавляется временная метка для отслеживания

**Зачем:**
- Мониторинг работоспособности сервиса
- Проверка доступности внешних зависимостей
- Используется системами оркестрации и мониторинга

### 5. Get Rates - Получение курсов валют

```python
@app.route("/rates")
def get_rates():
    global _exchange_cache, _cache_timestamp
    
    # Проверяем кэш
    if _cache_timestamp and (datetime.now().timestamp() - _cache_timestamp) < CACHE_TTL:
        return jsonify({
            "base": "USD",
            "rates": _exchange_cache,
            "cached": True
        })
    
    # Запрос к API
    try:
        response = requests.get(
            "https://api.exchangerate-api.com/v4/latest/USD",
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        # Обновляем кэш
        _exchange_cache = data.get("rates", {})
        _cache_timestamp = datetime.now().timestamp()
        
        return jsonify({
            "base": data.get("base", "USD"),
            "rates": _exchange_cache,
            "date": data.get("date"),
            "cached": False
        })
```

**Что делается пошагово:**

1. **Проверка кэша:**
   ```python
   if _cache_timestamp and (datetime.now().timestamp() - _cache_timestamp) < CACHE_TTL:
   ```
   - Проверяется, есть ли кэш и не истек ли он
   - `datetime.now().timestamp()` - текущее время в секундах
   - Если кэш валиден - возвращаем данные из кэша с флагом `cached: True`

2. **Запрос к внешнему API:**
   - Если кэш истек или отсутствует, делаем запрос
   - `response.raise_for_status()` - выбрасывает исключение при ошибке HTTP
   - `response.json()` - парсит JSON-ответ

3. **Обновление кэша:**
   - Сохраняем курсы в `_exchange_cache`
   - Обновляем `_cache_timestamp` текущим временем
   - Теперь следующие запросы будут использовать кэш

4. **Возврат результата:**
   - Возвращаем курсы с флагом `cached: False` (данные свежие)
   - Включаем дату обновления курсов

**Зачем кэширование:**
- Курсы валют обновляются не очень часто
- Кэш уменьшает нагрузку на внешний API
- Ускоряет ответ сервера
- Экономит трафик и ресурсы

**Проблемы in-memory кэша:**
- При перезапуске сервера кэш теряется
- Не работает при нескольких экземплярах приложения
- В production используют Redis или Memcached

### 6. Convert Currency - Конвертация валют

```python
@app.route("/convert/<float:amount>/<from_currency>/<to_currency>")
def convert_currency(amount, from_currency, to_currency):
    # Получаем курсы
    response = requests.get(...)
    rates = data.get("rates", {})
    
    # Конвертируем через USD
    if from_upper == "USD":
        result = amount * rates[to_upper]
    elif to_upper == "USD":
        result = amount / rates[from_upper]
    else:
        # Конвертируем: from -> USD -> to
        usd_amount = amount / rates[from_upper]
        result = usd_amount * rates[to_upper]
```

**Что делается пошагово:**

1. **Парсинг параметров из URL:**
   - `<float:amount>` - извлекает число из URL (например, `100.5`)
   - `<from_currency>` - код валюты источника (например, `USD`)
   - `<to_currency>` - код валюты назначения (например, `EUR`)
   - Пример URL: `/convert/100/USD/EUR`

2. **Получение курсов:**
   - Делается запрос к API для получения актуальных курсов
   - Все курсы относительно USD (базовая валюта)

3. **Логика конвертации:**

   **Случай 1: Из USD в другую валюту**
   ```python
   if from_upper == "USD":
       result = amount * rates[to_upper]
   ```
   - Просто умножаем на курс: 100 USD * 0.85 = 85 EUR

   **Случай 2: Из другой валюты в USD**
   ```python
   elif to_upper == "USD":
       result = amount / rates[from_upper]
   ```
   - Делим на курс: 100 EUR / 0.85 = 117.65 USD

   **Случай 3: Между двумя не-USD валютами**
   ```python
   usd_amount = amount / rates[from_upper]  # Сначала в USD
   result = usd_amount * rates[to_upper]    # Потом в целевую
   ```
   - Двухшаговая конвертация: EUR -> USD -> RUB
   - Это называется "кросс-курс"

4. **Обработка ошибок:**
   - Проверяется наличие валют в словаре курсов
   - Если валюта не найдена - возвращается ошибка 400

5. **Возврат результата:**
   - Округление до 2 знаков после запятой
   - Возвращается JSON с исходной суммой, валютами и результатом

**Зачем конвертация через USD:**
- API предоставляет курсы только относительно USD
- Для конвертации между другими валютами нужен промежуточный шаг
- Это стандартный подход в финансовых системах

### 7. Запуск приложения

```python
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
```

**Что делается:**
- `if __name__ == "__main__"` - код выполняется только при прямом запуске
- `host="0.0.0.0"` - сервер доступен извне (не только localhost)
- `port=5001` - порт для прослушивания
- `debug=True` - режим отладки (автоперезагрузка при изменениях)

**Зачем:**
- В production используют WSGI-серверы (Gunicorn, uWSGI)
- `debug=True` только для разработки (показывает детальные ошибки)

## Основные концепции Flask

### 1. Декораторы маршрутизации

```python
@app.route("/path")
def function():
    return jsonify({...})
```

- Декоратор `@app.route()` связывает URL с функцией
- Можно указать методы: `@app.route("/", methods=["GET", "POST"])`
- Можно использовать переменные: `@app.route("/user/<int:user_id>")`

### 2. Типы конвертеров URL

- `<int:variable>` - целое число
- `<float:variable>` - число с плавающей точкой
- `<str:variable>` - строка (по умолчанию)
- `<path:variable>` - путь (включает слэши)

### 3. jsonify vs json.dumps

```python
# Flask способ (правильный)
return jsonify({"key": "value"})

# Неправильный способ
return json.dumps({"key": "value"}), 200, {"Content-Type": "application/json"}
```

- `jsonify()` автоматически устанавливает заголовки
- Правильный Content-Type
- Правильная кодировка

### 4. Обработка ошибок

```python
except requests.RequestException as e:
    return jsonify({"error": "..."}), 503
```

- Можно вернуть статус код вторым аргументом
- 503 Service Unavailable - сервис временно недоступен
- 400 Bad Request - неверный запрос
- 404 Not Found - ресурс не найден

## Примеры использования

1. **Получить курсы валют:**
   ```
   GET /rates
   Ответ: {"base": "USD", "rates": {"EUR": 0.85, "RUB": 75.5, ...}, "cached": false}
   ```

2. **Конвертировать валюту:**
   ```
   GET /convert/100/USD/EUR
   Ответ: {"amount": 100, "from": "USD", "to": "EUR", "result": 85.0}
   ```

3. **Проверить здоровье:**
   ```
   GET /health
   Ответ: {"status": "healthy", "exchange_api_available": true, ...}
   ```

## Итоги

Этот пример демонстрирует:
- Создание REST API на Flask
- Работу с внешними API через `requests`
- Простое кэширование данных
- Конвертацию валют с кросс-курсами
- Обработку ошибок и возврат правильных HTTP-статусов
- Использование декораторов для маршрутизации
- Парсинг параметров из URL
