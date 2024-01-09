from django.contrib import admin
from .models import SubscriptionPlan, PlanCost, GuardianSubscription


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'grace_period')
    search_fields = ('id', 'translations__name', 'description')
    list_filter = ('grace_period', 'is_active', 'create_timestamp', 'update_timestamp')


@admin.register(PlanCost)
class PlanCostAdmin(admin.ModelAdmin):
    list_display = ('id', 'plan', 'recurrence_period', 'recurrence_unit', 'price')
    search_fields = ('id', 'plan__translations__name', 'recurrence_period', 'recurrence_unit', 'price')


@admin.register(GuardianSubscription)
class GuardianSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'guardian', 'subscription', 'date_billing_start',
                    'date_billing_end', 'date_billing_last', 'date_billing_next')
    search_fields = ('id', 'guardian__first_name', 'guardian__last_name', 'subscription')
    list_filter = ('subscription', 'date_billing_start', 'date_billing_end',
                   'date_billing_last', 'date_billing_next', 'is_active')
