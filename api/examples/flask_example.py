"""
Flask Example - рабочий веб-сервис для получения курсов валют
Демонстрирует: HTTP запросы, обработка ошибок, JSON ответы, роутинг
"""
import requests
from flask import Flask, jsonify
from datetime import datetime

app = Flask(__name__)

# Кэш для курсов валют (в реальном приложении использовать Redis)
_exchange_cache = {}
_cache_timestamp = None
CACHE_TTL = 3600  # 1 час


@app.route("/")
def root():
    """Главная страница"""
    return jsonify({
        "message": "Currency Exchange API",
        "endpoints": {
            "/rates": "Получить курсы валют",
            "/convert/<amount>/<from_currency>/<to_currency>": "Конвертировать валюту",
            "/health": "Проверка здоровья сервиса"
        }
    })


@app.route("/health")
def health_check():
    """Проверка доступности сервиса"""
    try:
        # Проверяем доступность внешнего API
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


@app.route("/rates")
def get_rates():
    """
    Получить актуальные курсы валют
    Делает реальный запрос к ExchangeRate API
    """
    global _exchange_cache, _cache_timestamp
    
    # Проверяем кэш
    if _cache_timestamp and (datetime.now().timestamp() - _cache_timestamp) < CACHE_TTL:
        return jsonify({
            "base": "USD",
            "rates": _exchange_cache,
            "cached": True
        })
    
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
        
    except requests.RequestException as e:
        return jsonify({
            "error": f"Не удалось получить курсы валют: {str(e)}"
        }), 503


@app.route("/convert/<float:amount>/<from_currency>/<to_currency>")
def convert_currency(amount, from_currency, to_currency):
    """
    Конвертировать валюту
    Пример: /convert/100/USD/EUR
    """
    try:
        # Получаем курсы
        response = requests.get(
            "https://api.exchangerate-api.com/v4/latest/USD",
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        rates = data.get("rates", {})
        
        # Конвертируем через USD
        from_upper = from_currency.upper()
        to_upper = to_currency.upper()
        
        if from_upper == "USD":
            if to_upper not in rates:
                return jsonify({"error": f"Валюта {to_upper} не найдена"}), 400
            result = amount * rates[to_upper]
        elif to_upper == "USD":
            if from_upper not in rates:
                return jsonify({"error": f"Валюта {from_upper} не найдена"}), 400
            result = amount / rates[from_upper]
        else:
            if from_upper not in rates or to_upper not in rates:
                return jsonify({"error": "Одна из валют не найдена"}), 400
            # Конвертируем: from -> USD -> to
            usd_amount = amount / rates[from_upper]
            result = usd_amount * rates[to_upper]
        
        return jsonify({
            "amount": amount,
            "from": from_upper,
            "to": to_upper,
            "result": round(result, 2)
        })
        
    except requests.RequestException as e:
        return jsonify({
            "error": f"Ошибка при конвертации: {str(e)}"
        }), 503


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
