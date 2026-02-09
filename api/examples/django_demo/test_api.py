#!/usr/bin/env python3
"""Простой скрипт для тестирования API"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

def test_endpoint(name, url):
    print(f"\n{'='*50}")
    print(f"Тестирую: {name}")
    print(f"URL: {url}")
    print('='*50)
    try:
        response = requests.get(url, timeout=15)
        print(f"Status Code: {response.status_code}")
        print(f"Response:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    print("Тестирование Django API\n")
    
    test_endpoint("Root", f"{BASE_URL}/")
    test_endpoint("Health Check", f"{BASE_URL}/health/")
    test_endpoint("My IP", f"{BASE_URL}/myip/")
    test_endpoint("IP Info (8.8.8.8)", f"{BASE_URL}/ip/8.8.8.8/")
    test_endpoint("IP Info (1.1.1.1)", f"{BASE_URL}/ip/1.1.1.1/")
