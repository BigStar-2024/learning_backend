from django.contrib import admin
from .models import Battery, Level
from parler import admin as parler_admin
from import_export.admin import ImportExportModelAdmin


@admin.register(Battery)
class BatteryAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'level')
    search_fields = ('id', 'student__first_name', 'student__last_name', 'student__full_name', 'level')
    list_filter = ('level', 'create_timestamp', 'update_timestamp')


@admin.register(Level)
class LevelAdmin(parler_admin.TranslatableAdmin):
    list_display = ('id', 'name', 'points_required', 'amount', 'is_active')
    search_fields = ('id', 'translations__name', 'points_required', 'amount')
    list_filter = ('points_required', 'amount', 'is_active', 'create_timestamp', 'update_timestamp')
