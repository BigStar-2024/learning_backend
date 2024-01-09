from django.contrib import admin
from import_export import admin as import_export_admin
from .models import Plan, GuardianStudentPlan, StudentPlan


@admin.register(Plan)
class PlanAdmin(import_export_admin.ImportExportModelAdmin):
    list_display = ('id', 'name', 'description', 'area_of_knowledge', 'price_month', 'price_preferential_month', 'quantity_preferential_month', 'price_year', 'price_preferential_year', 'quantity_preferential_year', 'currency', 'quantity_lower_limit')
    search_fields = ('id', 'name', 'description')
    list_filter = ('area_of_knowledge', 'currency', 'price_month', 'price_year',
                   'is_active', 'create_timestamp', 'update_timestamp')

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(GuardianStudentPlan)
class GuardianStudentPlanAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'guardian', 'plan', 'is_cancel', 'is_paid', 'expired_at')
    search_fields = ('id', 'student__first_name', 'student__last_name', 'student__full_name',
                     'guardian__first_name', 'guardian__last_name', 'order_detail__id')
    list_filter = ('plan', 'is_paid', 'is_cancel', 'expired_at', 'is_active', 'create_timestamp', 'update_timestamp')

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)


@admin.register(StudentPlan)
class StudentPlanAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'audience')
    search_fields = ('id', 'name', 'audience__translations__name')
    list_filter = ('topic_grade', 'is_active', 'create_timestamp', 'update_timestamp')
