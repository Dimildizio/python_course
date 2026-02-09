"""
Django Example - рабочий веб-сервис для получения информации о IP адресах
Демонстрирует: Django views, HTTP запросы, обработка ошибок, JSON ответы

Использование:
1. Создайте Django проект: django-admin startproject myproject
2. Создайте приложение: python manage.py startapp api
3. Скопируйте этот код в api/views.py
4. Добавьте в myproject/urls.py:
   from django.urls import path, include
   urlpatterns = [path('api/', include('api.urls'))]
5. Создайте api/urls.py с маршрутами (см. внизу файла)
"""
import requests
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods


@method_decorator(csrf_exempt, name='dispatch')
class RootView(View):
    """Главная страница API"""
    
    def get(self, request):
        return JsonResponse({
            "message": "IP Info API",
            "endpoints": {
                "/api/ip/<ip_address>": "Получить информацию об IP адресе",
                "/api/myip": "Получить информацию о своем IP",
                "/api/health": "Проверка здоровья сервиса"
            }
        })


@method_decorator(csrf_exempt, name='dispatch')
class HealthCheckView(View):
    """Проверка доступности сервиса"""
    
    def get(self, request):
        try:
            # Проверяем доступность внешнего API
            response = requests.get(
                "https://ipapi.co/json/",
                timeout=5
            )
            api_available = response.status_code == 200
        except Exception:
            api_available = False
        
        return JsonResponse({
            "status": "healthy",
            "ip_api_available": api_available
        })


@method_decorator(csrf_exempt, name='dispatch')
class IPInfoView(View):
    """
    Получить информацию об IP адресе
    Делает реальный запрос к ipapi.co
    """
    
    def get(self, request, ip_address):
        try:
            response = requests.get(
                f"https://ipapi.co/{ip_address}/json/",
                timeout=10
            )
            
            if response.status_code == 404:
                return JsonResponse(
                    {"error": f"IP адрес {ip_address} не найден"},
                    status=404
                )
            
            response.raise_for_status()
            data = response.json()
            
            # Возвращаем только нужные поля
            return JsonResponse({
                "ip": data.get("ip", ip_address),
                "city": data.get("city"),
                "region": data.get("region"),
                "country": data.get("country_name"),
                "country_code": data.get("country_code"),
                "timezone": data.get("timezone"),
                "org": data.get("org"),
                "latitude": data.get("latitude"),
                "longitude": data.get("longitude")
            })
            
        except requests.RequestException as e:
            return JsonResponse(
                {"error": f"Ошибка при запросе к IP API: {str(e)}"},
                status=503
            )


@method_decorator(csrf_exempt, name='dispatch')
class MyIPView(View):
    """
    Получить информацию о своем IP адресе
    Определяет IP клиента и возвращает информацию о нем
    """
    
    def get(self, request):
        # Получаем IP клиента
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        # Если IP не определен, используем API для определения
        if not ip or ip == "127.0.0.1":
            try:
                response = requests.get(
                    "https://api.ipify.org?format=json",
                    timeout=5
                )
                response.raise_for_status()
                ip = response.json().get("ip", "unknown")
            except Exception:
                return JsonResponse(
                    {"error": "Не удалось определить IP адрес"},
                    status=503
                )
        
        # Получаем информацию об IP
        try:
            response = requests.get(
                f"https://ipapi.co/{ip}/json/",
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            return JsonResponse({
                "ip": data.get("ip", ip),
                "city": data.get("city"),
                "region": data.get("region"),
                "country": data.get("country_name"),
                "country_code": data.get("country_code"),
                "timezone": data.get("timezone"),
                "org": data.get("org")
            })
            
        except requests.RequestException as e:
            return JsonResponse(
                {"error": f"Ошибка при запросе к IP API: {str(e)}"},
                status=503
            )


# Пример urls.py для Django приложения:
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.RootView.as_view(), name='root'),
    path('health/', views.HealthCheckView.as_view(), name='health'),
    path('ip/<str:ip_address>/', views.IPInfoView.as_view(), name='ip_info'),
    path('myip/', views.MyIPView.as_view(), name='my_ip'),
]
"""
