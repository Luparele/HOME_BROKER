from django.contrib import admin
from django.apps import apps
from .models import Favorite, PortfolioItem

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'ticker', 'name', 'added_at')
    search_fields = ('user__username', 'ticker', 'name')
    list_filter = ('added_at',)

@admin.register(PortfolioItem)
class PortfolioItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'ticker', 'name', 'quantity', 'added_at')
    search_fields = ('user__username', 'ticker', 'name')
    list_filter = ('added_at', 'updated_at')

# Automatiza o registro de todas as tabelas (models) no admin
models = apps.get_models()
for model in models:
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass
