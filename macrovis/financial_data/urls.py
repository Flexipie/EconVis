from django.urls import path
from . import views

app_name = 'financial_data'

urlpatterns = [
    path('', views.index, name='index'),
    path('api/financial-data/<str:country_code>/<str:indicator>/', views.get_financial_data, name='get_financial_data'),
]