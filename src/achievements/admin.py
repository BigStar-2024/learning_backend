from django.contrib import admin
from .models import Achievement
from parler import admin as parler_admin


@admin.register(Achievement)
class AchievementAdmin(parler_admin.TranslatableAdmin):
    list_display = ('id', 'name', 'slug', 'image', 'hex_color', 'level_required',
                    'engangement_points', 'coins_earned', 'is_active')
    search_fields = ('id', 'translations__name', 'hex_color')
    readonly_fields = ()

    filter_horizontal = ()
    list_filter = ('slug', 'level_required', 'engangement_points', 'coins_earned', 'is_active')
    fieldsets = ()
