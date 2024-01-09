from django.contrib import admin
from .models import Guardian, GuardianStudent


@admin.register(Guardian)
class GuardianAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'gender', 'user', 'coupon_code', 'has_order', 'is_active')
    search_fields = ('id', 'first_name', 'last_name', 'coupon_code__code')
    list_filter = ('gender', 'has_order', 'is_active', 'create_timestamp', 'update_timestamp')


@admin.register(GuardianStudent)
class GuardianStudent(admin.ModelAdmin):
    list_display = ('id', 'guardian', 'student')
    search_fields = ('guardian', 'student')

