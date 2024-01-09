from django.contrib import admin
from .models import profile


class AdminProfileInline(admin.StackedInline):
    model = profile
    can_delete = False


@admin.register(profile)
class profileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'role')
    search_fields = ('id', 'user__username', 'user__first_name', 'user__last_name')
    readonly_fields = ()

    filter_horizontal = ()
    list_filter = ('role',)
    fieldsets = ()
