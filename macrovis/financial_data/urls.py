from django.urls import path
from . import views

app_name = 'financial_data'

urlpatterns = [
    path('', views.index, name='index'),
    path('data/<str:country_code>/<str:indicator>/', views.get_financial_data, name='get_financial_data'),
    path('advanced-filters/', views.advanced_filters, name='advanced_filters'),
    path('api/filter/', views.filter_data, name='filter_data'),
    path('api/compare/', views.compare_countries, name='compare_countries'),
]