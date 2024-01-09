from django.contrib import admin
from .models import Game, GameCategory, PlayGameTransaction
from parler import admin as parler_admin
from import_export.admin import ImportExportModelAdmin
from .resources import GameResource, GameCategoryResource


@admin.register(Game)
class GameAdmin(ImportExportModelAdmin, parler_admin.TranslatableAdmin):
    resource_class = GameResource
    list_display = ('id', 'name', 'image', 'path', 'cost', 'play_stats', 'is_active')
    search_fields = ('id', 'translations__name', 'image', 'path', 'cost', 'play_stats')
    list_filter = ('cost', 'play_stats', 'is_active', 'create_timestamp', 'update_timestamp')


@admin.register(GameCategory)
class GameCategoryAdmin(ImportExportModelAdmin, parler_admin.TranslatableAdmin):
    resource_class = GameCategoryResource
    list_display = ('id', 'name', 'image', 'bg_color', 'is_active')
    search_fields = ('id', 'translations__name', 'bg_color')
    list_filter = ('bg_color', 'is_active', 'create_timestamp', 'update_timestamp')


@admin.register(PlayGameTransaction)
class PlayGameTransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'game')
    search_fields = ('id', 'game__translations__name')
