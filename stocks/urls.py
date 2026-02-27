from django.urls import path
from . import views
from django.views.generic import TemplateView

app_name = 'stocks'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('search/', views.search_stock, name='search_stock'),
    path('stock/<str:ticker>/', views.stock_detail, name='stock_detail'),
    path('favorite/toggle/', views.toggle_favorite, name='toggle_favorite'),
    path('api/stock/<str:ticker>/history/', views.api_stock_history, name='api_stock_history'),
    path('portfolio/', views.portfolio_view, name='portfolio'),
    path('portfolio/add/', views.add_to_portfolio, name='add_to_portfolio'),
    
    # PWA files
    path('sw.js', TemplateView.as_view(template_name='stocks/sw.js', content_type='application/javascript'), name='sw'),
    path('manifest.json', TemplateView.as_view(template_name='stocks/manifest.json', content_type='application/json'), name='manifest'),
]
