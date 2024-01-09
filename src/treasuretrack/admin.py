from django.contrib import admin
from .models import WeeklyTreasureLevel, WeeklyTreasure, StudentWeeklyTreasure, WeeklyTreasureTransaction


@admin.register(WeeklyTreasureLevel)
class WeeklyTreasureLevelAdmin(admin.ModelAdmin):
    ordering = ['level']
    list_display = ('id', 'name', 'level', 'coins_required', 'correct_questions_required', 'bonus_coins')
    search_fields = ('id', 'name', 'level', 'coins_required', 'correct_questions_required', 'bonus_coins')
    list_filter = ('bonus_collectible', 'level', 'bonus_coins',
                   'coins_required', 'correct_questions_required', 'is_active')


@admin.register(WeeklyTreasure)
class WeeklyTreasureAdmin(admin.ModelAdmin):
    ordering = ['level']
    list_display = ('id', 'level', 'coins_awarded')
    search_fields = ('id', 'level__name', 'level__level', 'coins_awarded')
    list_filter = ('level', 'coins_awarded', 'collectibles_awarded', 'is_active')


@admin.register(StudentWeeklyTreasure)
class StudentWeeklyTreasureAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'weekly_treasure')
    search_fields = ('id', 'student__first_name', 'student__last_name', 'student__full_name')
    list_filter = ('weekly_treasure', 'create_timestamp', 'update_timestamp')


@admin.register(WeeklyTreasureTransaction)
class WeeklyTreasureTransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'student_weekly_treasure')
    search_fields = ('student_weekly_treasure__student__full_name',
                     'student_weekly_treasure__weekly_treasure__level__name',
                     'student_weekly_treasure__weekly_treasure__level__level')
    list_filter = ('student_weekly_treasure__weekly_treasure', 'create_timestamp', 'update_timestamp')
