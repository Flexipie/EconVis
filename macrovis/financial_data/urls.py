from django.urls import path
from . import views

app_name = 'financial_data'

urlpatterns = [
    path('', views.index, name='index'),
    path('api/financial-data/<str:country_code>/<str:indicator>/', views.get_financial_data, name='get_financial_data'),
    path('favorites/add/', views.add_favorite, name='add_favorite'),
    path('favorites/list/', views.list_favorites, name='list_favorites'),
    path('favorites/load/<int:favorite_id>/', views.load_favorite, name='load_favorite'),
    path('favorites/delete/<int:favorite_id>/', views.delete_favorite, name='delete_favorite'),
    path('last-searches/add/', views.add_last_search, name='add_last_search'),
    path('last-searches/list/', views.list_last_searches, name='list_last_searches'),
    path('delete_last_searches/', views.delete_all_last_searches, name='delete_last_searches'),
    path('export/<str:country_code>/<str:indicator_code>/', views.export_financial_data, name='export_financial_data'),
]
