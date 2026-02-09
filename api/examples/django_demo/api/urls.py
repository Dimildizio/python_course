from django.urls import path
from . import views

urlpatterns = [
    path('', views.RootView.as_view(), name='root'),
    path('health/', views.HealthCheckView.as_view(), name='health'),
    path('ip/<str:ip_address>/', views.IPInfoView.as_view(), name='ip_info'),
    path('myip/', views.MyIPView.as_view(), name='my_ip'),
]
