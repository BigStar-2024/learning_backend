from django.contrib import admin
from django.forms import ModelForm
from .models import Order, OrderDetail, PaymentHistory, PaypalTransaction, CardTransaction, PaymentMethod, DiscountCode
from import_export import admin as import_export_admin

@admin.register(PaymentMethod)
class PaymentMethodAdmin(
        import_export_admin.ImportExportModelAdmin,
):
    list_display = (
            'id',
            'school',
            'teacher',
            'guardian',
            'card',
            'card_first_name',
            'card_last_name',
            'card_exp_year',
            'card_exp_month',
            'card_cvc',
            'country',
            'state',
            'city',
            'post_code',
            'phone',
            'is_default',
    )
    search_fields = [
            'school__name',
            'teacher__user__username',
            'guardian__user__username',
            'card_number',
            'card_first_name',
            'card_last_name',
            'card_exp_year',
            'card_exp_month',
            'card_cvc',
            'country',
            'state',
            'city',
            'post_code',
            'phone',
    ]
    list_filter = ('create_timestamp', 'update_timestamp', 'is_default', 'country')

    @admin.display(description='Card Number')
    def card(self, obj):
        str = None
        if(obj.card_number):
            card_leng = len(obj.card_number)
            first_4 = obj.card_number[0:4]
            last_4 = obj.card_number[card_leng-4:card_leng]
            str = f"{first_4} *** {last_4}"
        return str

@admin.register(CardTransaction)
class CardTransactionAdmin(
        import_export_admin.ImportExportModelAdmin,
):
        list_display = (
                'id',
                'order_detail',
                'session_id',
                'card',
                'card_exp_year',
                'card_exp_month',
                'card_cvc',
                'country',
                'city',
                'state',
                'post_code',
                'phone',
                'is_captured'
        )
        search_fields = [
                'id',
                'order_detail__id',
                'session_id',
                'card_number',
                'card_first_name',
                'card_last_name',
                'card_exp_year',
                'card_exp_month',
                'card_cvc',
                'country',
                'city',
                'state',
                'post_code',
                'phone',
                'is_captured'
        ]
        list_filter = ('create_timestamp', 'update_timestamp', 'country', 'is_captured')

        @admin.display(description='Card Number')
        def card(self, obj):
                str = None
                if(obj.card_number):
                        card_leng = len(obj.card_number)
                        first_4 = obj.card_number[0:4]
                        last_4 = obj.card_number[card_leng-4:card_leng]
                        str = f"{first_4} *** {last_4}"
                return str

class ReadOnlyDiscountCodeForm(ModelForm):
    class Meta:
        model = DiscountCode
        exclude=['percentage','type']

@admin.register(DiscountCode)
class DiscountCodeAdmin(
        import_export_admin.ImportExportModelAdmin,
):
    list_display = (
            'id',
            'code',
            'percentage',
            'trial_day',
            'expired_at',
            'stripe_coupon_id',
            'type',
            'for_who',
            'is_active',
    )
    def get_form(self, request, obj=None, **kwargs):
        if obj:
                kwargs['form'] = ReadOnlyDiscountCodeForm
                print("here is update object")
                
        return super(DiscountCodeAdmin, self).get_form(request, obj, **kwargs)
#     readonly_fields=('percentage', 'type',)

@admin.register(OrderDetail)
class OrderDetailAdmin(
        import_export_admin.ImportExportModelAdmin,
):
    list_display = (
        'id',
        'order',
        'school',
        'teacher',
        'guardian',
        'plan',
        'payment_method_plan_id',
        'quantity',
        'period',
        'discount',
        'total',
        'discount_code',
        'payment_method',
        'expired_at',
        'is_paid',
        'is_cancel',
        'on_discount',
    )
    list_filter = (
        'plan',
        'order__discount_code',
        'order__payment_method',
        'period',
        'is_paid',
        'is_cancel',
        'on_discount',
        'create_timestamp',
        'update_timestamp',
        )

    search_fields = [
        'id',
        'order__id',
        'order__guardian__user__username',
        'order__school__name',
        'order__teacher__user__username',
        'order__discount_code',
        'order__payment_method',
        'plan__name',
        'payment_method_plan_id',
        'subscription_id',
        'quantity',
        'period',
        'discount',
        'total',
        'expired_at',
        'status',
        ]
    search_help_text = "Search by id, order_id, order_guardian, order_school, order_teacher, discount code, plan_name, payment_method_plan_id, subscription_id, quantity, period, discount, total, expired_at, status"
    
    @admin.display(description='Teacher', ordering='order__teacher')
    def teacher(self, obj):
        if obj.order:
                return obj.order.teacher.user.username if obj.order.teacher is not None else None
        return None

    @admin.display(description='Guardian', ordering='order__guardian')
    def guardian(self, obj):
        if obj.order:

                return obj.order.guardian.user.username if obj.order.guardian is not None else None
        return None

    @admin.display(description='School', ordering='order__school')
    def school(self, obj):
        if obj.order:
                return obj.order.school
        return None
    @admin.display(description='Discount Code', ordering='order__discount_code')
    def discount_code(self, obj):
        if obj.order:
                return obj.order.discount_code
        return None
    @admin.display(description='Payment Method', ordering='order__payment_method')
    def payment_method(self, obj):
        if obj.order:
                return obj.order.payment_method
        return None


@admin.register(Order)
class OrderAdmin(
        import_export_admin.ImportExportModelAdmin,
):
    list_display = (
            'id',
            'guardian',
            'teacher',
            'school',
            'discount_code',
            'total',
            'payment_method',
            'is_paid',
    )
    list_filter = (
        'discount_code',
        'payment_method',
        'is_paid',
        'create_timestamp',
        'update_timestamp',
        )

    search_fields = [
        'id',
        'order__id',
        'order__guardian__user__username',
        'order__school__name',
        'order__teacher__user__username',
        'order__discount_code',
        'plan__name',
        'payment_method_plan_id',
        'subscription_id',
        'quantity',
        'period',
        'discount',
        'total',
        'expired_at',
        'status',
        ]

@admin.register(PaymentHistory)
class PaymentHistoryAdmin(
         import_export_admin.ImportExportModelAdmin,
):
        list_display = (
                'id',
                'type',
                'user',
                'order',
                'card',
                'amount',
                'message',
                'create_timestamp',
        )
        #--------------- Disable Editing -----------------------#
        list_display_links = None
        #--------------- Add Filter ----------------------------#
        list_filter = ('type',)
        #--------------- ADD Date Hierarcy ---------------------#
        date_hierarchy = 'create_timestamp'
        #--------------- ADD Search Field ----------------------#
        search_fields = ['user__email', 'card_number', 'type', 'order__id']
        #---------------#
        search_help_text = "Search by email, card number, order_id and type"

        @admin.display(description='Card Number', ordering='card_number')
        def card(self, obj):
                str = None
                if(obj.card_number):
                        card_leng = len(obj.card_number)
                        first_4 = obj.card_number[0:4]
                        last_4 = obj.card_number[card_leng-4:card_leng]
                        str = f"{first_4} *** {last_4}"
                return str

